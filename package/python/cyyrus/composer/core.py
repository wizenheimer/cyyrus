import importlib
import inspect
import tempfile
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
)

import pandas as pd
from datasets import Dataset, DatasetDict
from huggingface_hub.hf_api import HfApi

from cyyrus.composer.dataframe import (
    DataFrameUtils,
    ExportFormat,
)
from cyyrus.composer.dataset import DatasetUtils
from cyyrus.composer.markdown import MarkdownUtils
from cyyrus.composer.progress import conditional_tqdm
from cyyrus.constants.messages import Messages
from cyyrus.models.spec import Spec
from cyyrus.models.task import TaskType
from cyyrus.tasks.base import BaseTask
from cyyrus.tasks.default import DefaultTask
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


class Composer:
    def __init__(self, spec: Spec) -> None:
        logger.debug("Initializing Composer with Spec")
        self.spec: Spec = spec
        self.dataframe: pd.DataFrame = pd.DataFrame()

        logger.debug("Infering task artifacts")
        self.task_artifacts = self._infer_tasks()

        logger.debug(f"Discovered {len(self.task_artifacts)} total possible tasks")
        logger.debug("Composer initialized")

    def _infer_tasks(self) -> Dict[TaskType, Type[BaseTask]]:
        try:
            logger.debug("Importing tasks module")
            module = importlib.import_module("cyyrus.tasks")
        except ImportError as _:
            raise
        else:
            task_dict: Dict[TaskType, Type[BaseTask]] = {}

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if hasattr(cls, "TASK_ID") and (issubclass(cls, BaseTask)) and cls != BaseTask:
                    logger.debug(f"Registering task: {cls.TASK_ID} to task artifacts")
                    task_dict[cls.TASK_ID] = cls
                else:
                    logger.debug(f"Skipping class: {cls} from task artifacts")

            return task_dict

    def compose(
        self,
        dry_run: bool = False,
    ):
        logger.debug("Iterating over levels in the spec")
        # Iterate over each level in the spec
        for level_index, level in enumerate(self.spec.levels()):
            logger.debug(f"Processing level: {level_index}")
            # Merge tasks in the level
            for input_columns, output_column, task_type, task_properties in level:
                logger.debug(f"Processing task: {task_type}")

                if dry_run:
                    logger.info("Dry run enabled, skipping execution")
                    logger.info(f"Task: {task_type}")
                    logger.info(f"Inputs: {input_columns}")
                    logger.info(f"Output: {output_column}")
                    continue

                self.execute(
                    input_columns=input_columns,
                    output_column=output_column,
                    task_type=task_type,
                    task_properties=task_properties,
                    level_index=level_index,
                )

    def execute(
        self,
        input_columns: List[str],
        output_column: str,
        task_type: TaskType,
        task_properties: Dict[str, Any],
        level_index: int = 0,
        dry_run: bool = False,
    ):
        logger.info(f"Preparing column: {output_column}")
        logger.info(f"Executing task: {task_type}")
        logger.debug(f"Inputs: {input_columns}")
        logger.debug(f"Output: {output_column}")

        task_entity = self.task_artifacts.get(task_type, DefaultTask)
        task_instance = task_entity(
            column_name=output_column,
            task_properties=task_properties,
        )

        if dry_run:
            logger.info("Dry run enabled, skipping execution")
            logger.info(f"Task: {task_type}")
            logger.info(f"Input Columns: {input_columns[:2]}...")
            logger.info(f"Output Columns: {output_column}")
            return

        task_inputs = self._import_columns(columns=input_columns)

        task_results: List[Dict[str, Any]] = []
        # Incase there are no task_inputs we attempt reference free execution
        if not task_inputs and level_index == 0:
            logger.debug("No task inputs, attempting reference free execution")
            task_results: List[Dict[str, Any]] = task_instance.reference_free_execution()
        # Incase there are task_inputs we attempt reference based execution
        else:
            logger.debug("Task inputs found, attempting reference based execution")
            logger.debug(f"Total Task inputs: {len(task_inputs)}")
            for task_input in conditional_tqdm(
                task_inputs,
                use_tqdm=not dry_run,
            ):
                task_output = task_instance.reference_based_execution(task_input)
                task_results.append({**task_input, **task_output})

        self._refresh_dataframe(
            column_data=task_results,
        )

    def export(
        self,
        export_format: Union[ExportFormat, str],
        filepath: Union[str, Path],
    ) -> None:
        logger.debug(f"Exporting data in {export_format} format to {filepath}")

        # Validate and convert format to ExportFormat enum
        if isinstance(export_format, str):
            try:
                export_format = ExportFormat(export_format.lower())
            except ValueError:
                raise ValueError(f"Unsupported export format: {export_format}")

        # Validate and convert filepath to Path
        if isinstance(filepath, str):
            filepath = Path(filepath)

        # Ensure the directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Check if file already exists
        if filepath.exists():
            logger.warning(f"File {filepath} already exists. It will be overwritten.")

        try:
            # Prepare the data
            prepared_data = self._prepare(export_format)

            # Export the data
            if isinstance(prepared_data, DatasetDict) or isinstance(prepared_data, Dataset):
                logger.debug("Exporting Hugging Face DatasetDict")
                prepared_data.save_to_disk(filepath)
                readme_content = MarkdownUtils.generate_readme(
                    self.spec,
                    self.spec.dataset.metadata.name,
                    self.dataframe,
                )
                with open(f"{filepath}/README.md", "w") as readme_file:
                    readme_file.write(readme_content)

            elif isinstance(prepared_data, pd.DataFrame):
                if export_format == ExportFormat.JSON:
                    prepared_data.to_json(
                        filepath,
                        orient="records",
                        lines=True,
                    )
                elif export_format == ExportFormat.CSV:
                    prepared_data.to_csv(
                        filepath,
                        index=False,
                    )
                elif export_format == ExportFormat.PICKLE:
                    prepared_data.to_pickle(
                        filepath,
                    )
                elif export_format == ExportFormat.PARQUET:
                    prepared_data.to_parquet(
                        filepath,
                    )
            else:
                raise TypeError(f"Unsupported data type for exporting: {type(prepared_data)}")

            logger.info(f"Data successfully exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
            raise

    # Prepare the dataframe for export
    def _prepare(
        self,
        export_format: ExportFormat = ExportFormat.HUGGINGFACE,
    ) -> Union[DatasetDict, pd.DataFrame]:
        logger.debug(f"Preparing dataframe for {export_format} export")

        logger.debug("Handling flattening")
        df = DataFrameUtils.handle_flattening(
            self.dataframe,
            self.spec.dataset.attributes.flatten_columns,
        )

        # Handle nulls
        logger.debug("Attempting to handle nulls")
        df = DataFrameUtils.handle_nulls(
            self.dataframe,
            self.spec.dataset.attributes.nulls,
        )

        # Ensure unique columns
        logger.debug("Ensuring required columns")
        df = DataFrameUtils.ensure_required_columns(
            df,
            self.spec.dataset.attributes.required_columns,
        )

        # Ensure required columns
        logger.debug("Ensuring required columns")
        df = DataFrameUtils.ensure_unique_columns(
            df,
            self.spec.dataset.attributes.unique_columns,
        )

        # Remove unnecessary columns
        logger.debug("Removing unnecessary columns")
        df = DataFrameUtils.remove_columns(
            df=df,
            columns_to_remove=self.spec.dataset.attributes.exclude_columns,
        )

        if export_format == ExportFormat.HUGGINGFACE:
            # Convert to Hugging Face Dataset
            logger.debug("Converting dataframe to Hugging Face Dataset")
            dataset = Dataset.from_pandas(df)

            # Shuffle the dataset
            logger.debug("Shuffling the dataset")
            dataset = dataset.shuffle(seed=self.spec.dataset.shuffle.seed)

            # Split the dataset
            logger.debug("Splitting the dataset")
            train_set, test_set = DatasetUtils.split_dataset(
                dataset,
                self.spec.dataset.splits.train or 0.8,  # default to 0.8 if not specified
                self.spec.dataset.splits.test or 0.2,  # default to 0.2 if not specified
                self.spec.dataset.splits.seed or 42,  # default to 42 if not specified
            )

            # Create DatasetDict
            logger.debug("Creating DatasetDict with train and test splits")
            hf_dataset = DatasetDict(
                {
                    "train": train_set,
                    "test": test_set,
                },
            )

            # Set dataset metadata
            logger.debug("Setting dataset metadata")
            for split in hf_dataset.values():
                split.info.description = self.spec.dataset.metadata.description
                split.info.license = self.spec.dataset.metadata.license

            logger.debug("Export complete")
            return hf_dataset

        else:
            logger.debug(f"Preparing dataframe for {format} format")
            return df

    def _import_columns(
        self,
        columns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        This method exports column names from the dataframe. It:

        1. Exports all column names if column_names is None
        2. Exports only the specified column names if column_names is provided
        3. Returns the exported column names
        """
        logger.debug(f"Importing columns {columns[:2] if columns else None} from the dataframe")

        # Check if the dataframe is empty or no columns are specified
        if self.dataframe.empty or not columns:
            logger.debug("Dataframe is empty or no columns specified")
            return []

        # Check if all column names are valid
        logger.debug("Checking if all column names are valid")
        invalid_column_names = set(columns) - set(self.dataframe.columns)
        if invalid_column_names:
            # TODO: attempt to find the closest matching column names
            logger.error(Messages.INVALID_KEY_COLUMN)
            logger.error(f"Invalid column names: {invalid_column_names}")
            logger.error(f"Valid column names: {self.dataframe.columns}")
            raise ValueError(Messages.INVALID_KEY_COLUMN)

        # Export only the specified columns
        logger.debug("Exporting only the specified columns")
        result = [
            {k: v for k, v in row.items() if k in columns}
            for row in self.dataframe[columns].to_dict("records")  # type: ignore
            if all(pd.notna(v) for v in row.values())
        ]

        # Check if all rows were excluded due to NaN values
        logger.debug("Checking if all rows were excluded due to NaN values")
        if not result:
            logger.warning(Messages.ALL_ROWS_EXCLUDED_DUE_TO_NAN)

        logger.debug(f"Imported {len(result)} rows")
        return result

    def _refresh_dataframe(self, column_data: List[Dict[str, Any]]):
        """
        Refreshes the dataframe with new column data, handling potential duplicate indices and preserving existing data.

        :param column_data: List of dictionaries containing new data

        Strategy:
        If a column exists in both dataframes, we update it using combine_first.
        If a column only exists in the old dataframe, we keep it as is.
        If a column only exists in the new dataframe, we add it.
        """
        logger.debug("Refreshing dataframe with new column data")

        # Handle empty column data
        logger.debug("Handling empty column data")
        if not column_data:
            return

        # Convert column data to a DataFrame
        logger.debug("Converting column data to DataFrame")
        new_df = pd.DataFrame(column_data)

        # Explode list columns in new_df
        logger.debug("Exploding list columns in new dataframe")
        for col in new_df.columns:
            if new_df[col].apply(lambda x: isinstance(x, list)).any():
                new_df = new_df.explode(col)

        # Reset index of new_df to ensure it's unique
        new_df = new_df.reset_index(drop=True)

        # If the existing dataframe is empty, just use the new data
        logger.debug("Checking if the existing dataframe is empty")

        if self.dataframe.empty:
            logger.debug("Existing dataframe is empty, swapping previous dataframe")
            self.dataframe = new_df
            return

        # Reset index of existing dataframe to ensure it's unique
        logger.debug("Resetting index of existing dataframe")
        self.dataframe = self.dataframe.reset_index(drop=True)

        # Identify new columns
        logger.debug("Identifying new columns")
        existing_columns = set(self.dataframe.columns)

        # Create a temporary dataframe with all columns
        logger.debug("Creating a temporary dataframe with all columns")
        temp_df = pd.DataFrame(index=range(max(len(self.dataframe), len(new_df))))

        # Update existing columns and add new ones
        logger.debug("Updating existing columns and adding new ones")
        for col in self.dataframe.columns.union(new_df.columns):
            if col in existing_columns and col in new_df.columns:
                # Update existing column, preserving old values where new ones are NaN
                temp_df[col] = new_df[col].combine_first(self.dataframe[col])
            elif col in existing_columns:
                # Keep existing column as is
                temp_df[col] = self.dataframe[col]
            else:
                # Add new column
                temp_df[col] = new_df[col]

        # Update self.dataframe with the merged data
        logger.debug("Updating self.dataframe with the merged data")
        self.dataframe = temp_df.dropna(how="all").reset_index(drop=True)

        logger.debug("Dataframe refreshed")

    def publish(
        self,
        repository_id: str,
        huggingface_token: str,
        private: bool = False,
    ):
        logger.info(f"Publishing dataset to Hugging Face: {repository_id}")

        try:
            # Prepare the dataset
            hf_dataset: DatasetDict = self._prepare(ExportFormat.HUGGINGFACE)  # type: ignore

            # Initialize Hugging Face API
            api = HfApi(token=huggingface_token)

            # Create or update the dataset on Hugging Face
            api.create_repo(
                repo_id=repository_id,
                repo_type="dataset",
                exist_ok=True,
                private=private,
            )

            # # Save the dataset to a temporary directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Save the dataset to the temporary directory
                hf_dataset.save_to_disk(tmp_dir)

                # Generate the README file
                readme_content = MarkdownUtils.generate_readme(
                    self.spec,
                    repository_id,
                    self.dataframe,
                )
                with open(f"{tmp_dir}/README.md", "w") as readme_file:
                    readme_file.write(readme_content)

                # Upload the dataset files
                api.upload_folder(
                    repo_id=repository_id,
                    folder_path=tmp_dir,
                    repo_type="dataset",
                    multi_commits=True,
                )

            logger.info(f"Dataset successfully published to {repository_id}")
        except Exception as e:
            logger.error(f"Failed to publish dataset: {str(e)}")
            raise

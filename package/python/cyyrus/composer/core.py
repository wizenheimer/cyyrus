import importlib
import inspect
import warnings
from collections import defaultdict
from typing import (
    Any,
    DefaultDict,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
)

import pandas as pd
from datasets import Dataset, DatasetDict
from pydantic.main import BaseModel, create_model

from cyyrus.composer.dataframe import (
    ensure_required_columns,
    ensure_unique_columns,
    handle_nulls,
    split_dataset,
)
from cyyrus.errors.composer import (
    AllRowsExcludedDueToNanWarning,
    InvalidKeyColumnError,
    KeyColumnNotFoundError,
)
from cyyrus.models.spec import Spec
from cyyrus.models.task import TaskType
from cyyrus.tasks.base import BaseTask


class Composer:
    def __init__(self, spec: Spec) -> None:
        self.spec: Spec = spec
        self.dataframe: pd.DataFrame = pd.DataFrame()
        self.task_artifacts = self._infer_tasks()

    def _infer_tasks(
        self,
    ) -> DefaultDict[str, Type[BaseTask]]:
        try:
            module = importlib.import_module("cyyrus.tasks")
        except ImportError:
            raise
        else:
            from cyyrus.tasks.base import BaseTask
            from cyyrus.tasks.default import DefaultTask

            task_dict = defaultdict(lambda: DefaultTask)

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if (hasattr(cls, "TASK_ID") and issubclass(cls, BaseTask)) and cls != BaseTask:
                    task_dict[cls.TASK_ID] = cls  # type: ignore

            return task_dict  # type: ignore

    def compose(
        self,
        dry_run: bool = False,
    ):
        # Iterate over each level in the spec
        for level_index, level in enumerate(self.spec.levels()):

            # Merge tasks in the level
            task_groups = self._group_tasks(level)

            # Iterate over each task_dump in the merged_task_list
            for task_group in task_groups:
                self.execute(
                    task_group,
                    level_index,
                    dry_run,
                )

    def _group_tasks(
        self,
        level: List[
            Tuple[
                str,
                TaskType,
                Dict[str, int | str | float],
                Dict[str, str],
                Any | None,
            ],
        ],
    ) -> List[Dict[str, Any]]:  # type: ignore
        task_groups = defaultdict(
            lambda: {
                "columns": [],
                "models": {},
                "output_columns": [],
                "input_columns": [],
                "task_type": None,
                "task_properties": {},
            }
        )

        # Iterate over each task in the level, and group them by task type, properties, and input
        for column_name, task_type, task_properties, task_input, dynamic_model in level:
            # Create a unique key for each bucket
            key = (task_type, frozenset(task_properties.items()), frozenset(task_input.items()))

            # Column Parameters
            task_groups[key]["output_columns"].append(column_name)  # type: ignore
            task_groups[key]["input_columns"] = task_input.keys()  # type: ignore

            # Task Parameters
            task_groups[key]["task_type"] = task_type  # type: ignore
            task_groups[key]["task_properties"] = task_properties

            # Add dynamic model to the bucket
            if dynamic_model:
                task_groups[key]["models"][column_name] = dynamic_model  # type: ignore

        return list(task_groups.values())

    def execute(
        self,
        task_group: Dict[str, Any],
        level_index: int,
        dry_run: bool = False,
    ):
        task_type = task_group["task_type"]
        task_properties = task_group["task_properties"]

        origin_models = task_group["models"]
        nested_model = (
            self._nest_model(
                origin_models,
                task_group["task_type"],
                level_index,
            )
            if origin_models
            else None
        )

        task_instance = self.task_artifacts[task_type](
            task_properties=task_properties,
            task_model=nested_model,
        )

        input_columns = task_group["input_columns"]
        task_inputs = self._import_columns(columns=input_columns)

        if dry_run:
            return

        task_results = []
        for task_input in task_inputs:
            task_output = task_instance.execute(task_input)
            flattened_output = self._unnest_model(task_output, origin_models)
            merged_output = task_input | flattened_output
            task_results.append(merged_output)

        self._merge_columns(
            column_data=task_results,
            key_columns=input_columns,
        )

    def _nest_model(
        self,
        origin_models: Dict[str, BaseModel],
        task_type: str,
        level_index: int,
    ) -> BaseModel:
        model_name = f"Level{level_index}_{task_type.capitalize()}Model"
        return create_model(model_name, **{name: (model, ...) for name, model in origin_models.items()})  # type: ignore

    def _unnest_model(
        self,
        nested_instance: BaseModel,
        origin_models: Dict[str, Type[BaseModel]],
    ) -> Dict[str, BaseModel]:
        """
        Take an instance of a nested model and a list of model classes,
        and return instances of those individual models.

        :param nested_instance: An instance of a nested Pydantic model
        :param models: A list of Pydantic model classes to unnest
        :return: A dictionary of unnested model instances
        """

        unnested = {}
        for model_name in origin_models.keys():
            field_name = model_name
            if hasattr(nested_instance, field_name):
                unnested[field_name] = getattr(nested_instance, field_name).dict()
        return unnested

    def export(
        self,
    ) -> DatasetDict:
        # Handle nulls
        df = handle_nulls(self.dataframe, self.spec.dataset.attributes.nulls)

        # Ensure required columns and unique columns
        df = ensure_required_columns(df, self.spec.dataset.attributes.required_columns)
        df = ensure_unique_columns(df, self.spec.dataset.attributes.unique_columns)

        # Convert to Hugging Face Dataset
        dataset = Dataset.from_pandas(df)

        # Shuffle the dataset
        dataset = dataset.shuffle(seed=self.spec.dataset.shuffle.seed)

        # Split the dataset
        train_set, test_set = split_dataset(
            dataset,
            self.spec.dataset.splits.train or 0.8,  # default to 0.8 if not specified
            self.spec.dataset.splits.test or 0.2,  # default to 0.2 if not specified
            self.spec.dataset.splits.seed or 42,  # default to 42 if not specified
        )

        # Create DatasetDict
        hf_dataset = DatasetDict(
            {
                "train": train_set,
                "test": test_set,
            },
        )

        # Set dataset metadata
        for split in hf_dataset.values():
            split.info.description = self.spec.dataset.metadata.description
            split.info.license = self.spec.dataset.metadata.license

        return hf_dataset

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
        # Check if the dataframe is empty or no columns are specified
        if self.dataframe.empty or not columns:
            return []

        # Check if all column names are valid
        invalid_column_names = set(columns) - set(self.dataframe.columns)
        if invalid_column_names:
            raise InvalidKeyColumnError(
                extra_info={
                    "invalid_column_names": list(invalid_column_names),
                    "valid_column_names": list(self.dataframe.columns),
                }
            )

        # Export only the specified columns
        result = [
            {k: v for k, v in row.items() if k in columns}
            for row in self.dataframe[columns].to_dict("records")  # type: ignore
            if all(pd.notna(v) for v in row.values())
        ]

        # Check if all rows were excluded due to NaN values
        if not result:
            warnings.warn(AllRowsExcludedDueToNanWarning())

        return result

    def _merge_columns(
        self,
        column_data: List[Dict[str, Any]],
        key_columns: List[str],
    ):
        """
        Update an existing DataFrame with new columns from new_data,
        using key_columns to determine where to merge the new information.

        :param df_existing: Existing DataFrame to update
        :param new_data: List of dictionaries containing new data
        :param key_columns: List of column names to use as keys for merging
        :return: Updated DataFrame
        """
        # Convert column_data to a DataFrame
        df_new = pd.DataFrame(column_data)

        # Validate key_columns
        if not set(key_columns).issubset(self.dataframe.columns) or not set(key_columns).issubset(
            df_new.columns
        ):
            raise KeyColumnNotFoundError(
                extra_info={
                    "key_columns": key_columns,
                    "existing_columns": self.dataframe.columns,
                    "new_columns": df_new.columns,
                }
            )

        # Perform a left merge to update existing rows and add new columns
        self.dataframe = self.dataframe.merge(df_new, on=key_columns, how="left")

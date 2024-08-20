import importlib
import inspect
import warnings
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
)

import pandas as pd
from datasets import Dataset, DatasetDict

from cyyrus.composer.dataframe import (
    DataFrameUtils,
    DatasetUtils,
)
from cyyrus.errors.composer import (
    AllRowsExcludedDueToNanWarning,
    InvalidKeyColumnError,
)
from cyyrus.models.spec import Spec
from cyyrus.models.task import TaskType
from cyyrus.tasks.base import BaseTask
from cyyrus.tasks.default import DefaultTask


class Composer:
    def __init__(self, spec: Spec) -> None:
        self.spec: Spec = spec
        self.dataframe: pd.DataFrame = pd.DataFrame()
        self.task_artifacts = self._infer_tasks()

    def _infer_tasks(
        self,
    ) -> Dict[TaskType, Type[BaseTask]]:
        try:
            module = importlib.import_module("cyyrus.tasks")
        except ImportError:
            raise
        else:

            task_dict: Dict[TaskType, Type[BaseTask]] = {}

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if hasattr(cls, "TASK_ID") and (issubclass(cls, BaseTask)) and cls != BaseTask:
                    task_dict[cls.TASK_ID] = cls

            return task_dict

    def compose(
        self,
        dry_run: bool = False,
    ):
        # Iterate over each level in the spec
        for level_index, level in enumerate(self.spec.levels()):
            # Merge tasks in the level
            for input_columns, output_column, task_type, task_properties in level:
                self.execute(
                    input_columns=input_columns,
                    output_column=output_column,
                    task_type=task_type,
                    task_properties=task_properties,
                )

    def execute(
        self,
        input_columns: List[str],
        output_column: str,
        task_type: TaskType,
        task_properties: Dict[str, Any],
        dry_run: bool = False,
    ):
        task_entity = self.task_artifacts.get(task_type, DefaultTask)
        task_instance = task_entity(
            column_name=output_column,
            task_properties=task_properties,
        )

        task_inputs = self._import_columns(columns=input_columns)

        if dry_run:
            print(
                f"Task: {task_type}, Inputs: {task_inputs}, Properties: {task_properties}, Output: {output_column}\n"
            )
            return

        task_results = []
        if len(task_inputs) == 0:
            task_output = task_instance.execute({})
        else:
            for task_input in task_inputs:
                task_output = task_instance.execute(task_input)
                task_results.extend(task_output)

        self._merge_columns(
            column_data=task_results,
        )

    def export(
        self,
    ) -> DatasetDict:
        # Handle nulls
        df = DataFrameUtils.handle_nulls(self.dataframe, self.spec.dataset.attributes.nulls)

        # Ensure required columns and unique columns
        df = DataFrameUtils.ensure_required_columns(
            df, self.spec.dataset.attributes.required_columns
        )
        df = DataFrameUtils.ensure_unique_columns(df, self.spec.dataset.attributes.unique_columns)

        # Convert to Hugging Face Dataset
        dataset = Dataset.from_pandas(df)

        # Shuffle the dataset
        dataset = dataset.shuffle(seed=self.spec.dataset.shuffle.seed)

        # Split the dataset
        train_set, test_set = DatasetUtils.split_dataset(
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
    ):
        # Handle empty column data
        if not column_data:
            return

        new_df = pd.DataFrame(column_data)

        # Handle empty existing dataframe
        if self.dataframe.empty:
            self.dataframe = new_df
            return

        # Ensure the new DataFrame has the same number of rows as the original
        max_rows = max(len(self.dataframe), len(new_df))
        self.dataframe = self.dataframe.reindex(range(max_rows))
        new_df = new_df.reindex(range(max_rows))

        # Add new columns to the original DataFrame
        for column in new_df.columns:
            self.dataframe[column] = new_df[column]

        return self.dataframe

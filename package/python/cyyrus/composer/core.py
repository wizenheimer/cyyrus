import warnings
from collections import defaultdict
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Type, Union

import pandas as pd
from datasets import Dataset, DatasetDict
from pydantic.main import BaseModel

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
from cyyrus.models.types import create_nested_model


class TaskInfo(NamedTuple):
    task_type: str
    task_properties: Tuple[Tuple[str, Union[int, str, float]], ...]
    task_input: Tuple[Tuple[str, str], ...]


class Composer:
    def __init__(self, spec: Spec) -> None:
        self.spec: Spec = spec
        self.dataframe: pd.DataFrame = pd.DataFrame()

    def compose(self):
        """
        This method is the main entry point for composing nested models. It:

        1. Iterates through each level of the specification
        2. Creates nested models for each level
        3. Prints detailed information about each nested model
        """
        for level_index, level in enumerate(self.spec.levels()):
            nested_models = self._create_nested_models_for_level(level, level_index)
            for task_info, model in nested_models.items():
                print(f"Level: {level_index}")
                print(f"Task Type: {task_info.task_type}")
                print(f"Task Properties: {dict(task_info.task_properties)}")
                print(f"Task Input: {dict(task_info.task_input)}")
                print(f"Nested model: {model.__name__}")
                print(f"Fields: {model.model_fields.keys()}")
                print("---")

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

    def _create_nested_models_for_level(
        self,
        task_info_list: List[
            Tuple[str, TaskType, Dict[str, Union[int, str, float]], Dict[str, str], Any]
        ],
        level_index: int,
    ) -> Dict[TaskInfo, Type[BaseModel]]:
        """
        This method does the heavy lifting of creating nested models for a single level. It:

        1. Groups columns by their associated tasks
        2. Creates a nested model for each group of columns with the same task
        3. Returns a dictionary mapping TaskInfo objects to their corresponding nested models
        """
        grouped_columns = defaultdict(list)
        models = {}
        task_infos = {}

        for column_name, task_type, task_properties, task_input, dynamic_model in task_info_list:
            task_key = TaskInfo(
                task_type=task_type,
                task_properties=tuple(sorted(task_properties.items())),
                task_input=tuple(sorted(task_input.items())),
            )
            grouped_columns[task_key].append(column_name)
            if dynamic_model:
                models[column_name] = dynamic_model
            task_infos[task_key] = task_key

        nested_models = {}
        for task_key, columns in grouped_columns.items():
            task_models = {col: models[col] for col in columns if col in models}
            if task_models:
                nested_model = self._create_nested_model(task_models, task_key, level_index)
                nested_models[task_infos[task_key]] = nested_model

        return nested_models

    def _create_nested_model(
        self,
        models: Dict[str, Type[BaseModel]],
        task_key: TaskInfo,
        level_index: int,
    ) -> Type[BaseModel]:
        """
        This method creates a single nested model. It:

        1. Generates a descriptive name for the model based on the level, task, and columns
        2. Calls create_nested_model to create the actual Pydantic model
        3. Returns the created model
        """
        # Create a descriptive name for the nested model
        column_names = "_".join(sorted(models.keys()))
        task_name = task_key.task_type.lower()
        model_name = f"Level{level_index}_{task_name.capitalize()}Model_{column_names}"

        # Truncate the name if it's too long
        if len(model_name) > 100:
            model_name = model_name[:97] + "..."

        return create_nested_model(models, model_name)

    def _export_column_names(
        self,
        columns_to_export: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        This method exports column names from the dataframe. It:

        1. Exports all column names if column_names is None
        2. Exports only the specified column names if column_names is provided
        3. Returns the exported column names
        """
        # Check if the dataframe is empty or no columns are specified
        if self.dataframe.empty or not columns_to_export:
            return []

        # Check if all column names are valid
        invalid_column_names = set(columns_to_export) - set(self.dataframe.columns)
        if invalid_column_names:
            raise InvalidKeyColumnError(
                extra_info={
                    "invalid_column_names": list(invalid_column_names),
                    "valid_column_names": list(self.dataframe.columns),
                }
            )

        # Export only the specified columns
        result = [
            {k: v for k, v in row.items() if k in columns_to_export}
            for row in self.dataframe[columns_to_export].to_dict("records")  # type: ignore
            if all(pd.notna(v) for v in row.values())
        ]

        # Check if all rows were excluded due to NaN values
        if not result:
            warnings.warn(AllRowsExcludedDueToNanWarning())

        return result

    def _merge_column(
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

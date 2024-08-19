import importlib
import inspect
import warnings
from collections import defaultdict
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
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
)
from cyyrus.models.spec import Spec
from cyyrus.models.task import TaskType
from cyyrus.models.types import (
    StaticArrayModel,
    StaticBooleanModel,
    StaticFloatModel,
    StaticIntegerModel,
    StaticStringModel,
)
from cyyrus.tasks.base import DynamicBaseTask, StaticBaseTask
from cyyrus.tasks.default import DefaultTask


class Composer:
    def __init__(self, spec: Spec) -> None:
        self.spec: Spec = spec
        self.dataframe: pd.DataFrame = pd.DataFrame()
        self.task_artifacts = self._infer_tasks()
        self.groupable_task_types: Set[str] = {
            TaskType.GENERATION,
        }

    def _infer_tasks(
        self,
    ) -> Dict[TaskType, Type[StaticBaseTask | DynamicBaseTask]]:
        try:
            module = importlib.import_module("cyyrus.tasks")
        except ImportError:
            raise
        else:
            from cyyrus.tasks.base import DynamicBaseTask, StaticBaseTask

            task_dict: Dict[TaskType, Type[StaticBaseTask | DynamicBaseTask]] = {}

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if (
                    hasattr(cls, "TASK_ID")
                    and (issubclass(cls, StaticBaseTask))
                    or issubclass(cls, DynamicBaseTask)
                ) and (cls != StaticBaseTask or cls != DynamicBaseTask):
                    task_dict[cls.TASK_ID] = cls

            return task_dict

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
                List[str],
                Any | None,
            ]
        ],
    ) -> List[Dict[str, Any]]:
        grouped_tasks = defaultdict(
            lambda: {
                "input_columns": [],
                "output_columns": [],
                "origin_models": {},
                "task_type": TaskType.DEFAULT,
                "task_properties": {},
            }
        )
        ungrouped_tasks = []

        # Iterate over each task in the level, and group them by task type, properties, and input
        for task in level:
            column_name, task_type, task_properties, task_input, dynamic_model = task

            if task_type in self.groupable_task_types:
                key = (task_type, frozenset(task_properties.items()), frozenset(task_input))
                group = grouped_tasks[key]
                group["output_columns"].append(column_name)  # type: ignore
                group["input_columns"] = task_input  # type: ignore
                group["task_type"] = task_type
                group["task_properties"] = task_properties

                if dynamic_model:
                    group["origin_models"][column_name] = dynamic_model  # type: ignore
            else:
                ungrouped_tasks.append(
                    {
                        "output_columns": [column_name],
                        "input_columns": task_input,
                        "origin_models": {column_name: dynamic_model} if dynamic_model else {},
                        "task_type": task_type,
                        "task_properties": task_properties,
                    }
                )

        return list(grouped_tasks.values()) + ungrouped_tasks

    def execute(
        self,
        task_group: Dict[str, Any],
        level_index: int,
        dry_run: bool = False,
    ):
        # Extract task information
        task_type = task_group["task_type"]
        task_properties = task_group["task_properties"]
        input_columns = task_group["input_columns"]
        origin_models = task_group["origin_models"]
        output_columns = task_group["output_columns"]

        # Create a nested model if there are origin models
        nested_model = self._nest_model(
            origin_models,
            task_type,
            level_index,
        )

        task_entity = self.task_artifacts.get(task_type, DefaultTask)
        task_instance = task_entity(
            task_properties=task_properties,
            task_model=nested_model,  # type: ignore
        )

        # Import or generate columns based on the task type
        task_inputs = (
            self._import_columns(columns=input_columns)
            if task_type is not TaskType.PARSING and input_columns
            else self._generate_columns(upper_bound=task_properties.get("upper_bound", -1))
        )

        if dry_run:
            print(
                f"Task Type: {task_type}, Task Properties: {task_properties}, Task Inputs: {task_inputs}, Task Output: {output_columns}, Origin Models: {origin_models}, Nested Model: {nested_model}, Level Index: {level_index}"
            )
            return

        task_results = []
        for task_input in task_inputs:
            task_output = task_instance.execute(task_input)
            flattened_output = self._unnest_model(
                task_output,
                origin_models,
                output_columns,
                task_type,
            )
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
    ) -> (
        BaseModel
        | StaticIntegerModel
        | StaticFloatModel
        | StaticBooleanModel
        | StaticStringModel
        | StaticArrayModel
    ):
        model_name = f"Level{level_index}_{task_type.capitalize()}Model"
        return (
            create_model(
                model_name, **{name: (model, ...) for name, model in origin_models.items()}  # type: ignore
            )
            if task_type in self.groupable_task_types
            else list(origin_models.values())[0]
        )

    def _unnest_model(
        self,
        nested_instance: BaseModel,
        origin_models: Dict[str, Type[BaseModel]],
        output_columns: List[str],
        task_type: str,
    ) -> Dict[str, BaseModel]:
        unnested = {}
        if len(output_columns) == 1 and task_type not in self.groupable_task_types:
            unnested = nested_instance.model_dump()
            return {output_columns[0]: unnested.get("value", unnested)}

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

    def _generate_columns(
        self,
        upper_bound: int = -1,
    ) -> List[Dict[str, Any]]:
        return [{"path": "path/to/file"}]

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
        # Convert column_data to a DataFrame
        df_new = pd.DataFrame(column_data)

        if not key_columns:
            warnings.warn("key_columns is empty. Adding new columns without merging.", UserWarning)
            self._add_new_columns(df_new)
            return

        # Validate key_columns
        if not set(key_columns).issubset(self.dataframe.columns) or not set(key_columns).issubset(
            df_new.columns
        ):
            warnings.warn(
                f"Some key columns not found in both DataFrames. Key columns: {key_columns}. Adding new columns without merging.",
                UserWarning,
            )
            self._add_new_columns(df_new)
        else:
            self.dataframe = self.dataframe.merge(df_new, on=key_columns, how="left")

    def _add_new_columns(self, df_new):
        # Add new columns to the existing DataFrame
        for col in df_new.columns:
            if col not in self.dataframe.columns:
                self.dataframe[col] = None

        # Update the DataFrame with new data
        self.dataframe.update(df_new)

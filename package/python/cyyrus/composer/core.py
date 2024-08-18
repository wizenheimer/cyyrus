from collections import defaultdict
from pydantic.main import BaseModel
from cyyrus.models.task import TaskType
from typing import Any, Dict, List, NamedTuple, Tuple, Type, Union
from cyyrus.models.spec import Spec
from cyyrus.models.types import create_nested_model


class TaskInfo(NamedTuple):
    task_type: str
    task_properties: Tuple[Tuple[str, Union[int, str, float]], ...]
    task_input: Tuple[Tuple[str, str], ...]


class Composer:
    def __init__(self, spec: Spec) -> None:
        self.spec: Spec = spec

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

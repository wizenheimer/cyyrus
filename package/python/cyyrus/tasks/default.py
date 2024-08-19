from typing import Any, Dict

from pydantic.main import BaseModel

from cyyrus.models.task import TaskType
from cyyrus.models.types import (
    StaticArrayModel,
    StaticBooleanModel,
    StaticFloatModel,
    StaticIntegerModel,
    StaticStringModel,
    get_static_model,
)


class DefaultTask:
    TASK_ID = TaskType.DEFAULT

    def __init__(
        self,
        task_properties: Dict[str, Any],
        task_model: (
            BaseModel
            | StaticIntegerModel
            | StaticFloatModel
            | StaticBooleanModel
            | StaticStringModel
            | StaticArrayModel
        ),
    ) -> None:
        self.task_properties = task_properties
        self.task_model = get_static_model(TaskType.DEFAULT).model_construct(values="Default Task")

    def execute(
        self,
        task_input: Dict[str, Any],
    ):
        return self.task_model.model_construct(
            value=self._execute(
                task_input,
            )
        )

    def _execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        return f"Default Task: {task_input} with Task Properties: {self.task_properties}"

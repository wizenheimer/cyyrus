from abc import ABC, abstractmethod
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


class BaseTask(ABC):

    def __init__(
        self,
        task_properties: Dict[str, Any],
    ) -> None:
        self.task_properties = task_properties

    @abstractmethod
    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        pass


class DynamicBaseTask(BaseTask):
    TASK_ID = TaskType.BASE_DYNAMIC

    def __init__(
        self,
        task_properties: Dict[str, Any],
        task_model: BaseModel,
    ) -> None:
        super().__init__(task_properties)
        self.task_model = task_model if task_model else get_static_model(TaskType.GENERATION)

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        return self._execute(
            task_input,
        )

    @abstractmethod
    def _execute(
        cls,
        task_input: Dict[str, Any],
    ) -> Any:
        return f"Dynamic Task: {task_input} with Task Properties: {cls.task_properties}"


class StaticBaseTask(BaseTask):
    TASK_ID = TaskType.BASE_STATIC

    def __init__(
        self,
        task_properties: Dict[str, Any],
        task_model: (
            StaticIntegerModel
            | StaticFloatModel
            | StaticBooleanModel
            | StaticStringModel
            | StaticArrayModel
        ),
    ) -> None:
        super().__init__(task_properties)
        self.task_model = task_model

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        return self.task_model.model_construct(
            value=self._execute(
                task_input,
            )
        )

    @abstractmethod
    def _execute(
        cls,
        task_input: Dict[str, Any],
    ) -> Any:
        return f"Static Task: {task_input} with Task Properties: {cls.task_properties}"

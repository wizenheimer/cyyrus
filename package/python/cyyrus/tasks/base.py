from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTask(ABC):
    TASK_ID = "base_task"

    def __init__(
        self,
        task_properties: Dict[str, Any],
        task_model: Optional[Any] = None,
    ) -> None:
        self.task_properties = task_properties
        self.task_model = task_model

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        return self._execute(task_input)

    @abstractmethod
    def _execute(
        cls,
        task_input: Dict[str, Any],
    ) -> Any:
        pass

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTask(ABC):
    TASK_ID = "base_task"

    def __init__(
        self,
        task_properties: Dict[str, Any],
        task_model: Optional[Any] = None,
    ) -> None:
        super().__init__()

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        # TODO: trigger self._execute() method using the task_input
        # TODO: merge it with the task_inputs
        # TODO: return the merged result
        pass

    @abstractmethod
    def _execute(
        cls,
        task_input: Dict[str, Any],
    ):
        pass

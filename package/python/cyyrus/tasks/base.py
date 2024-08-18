from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseTask(ABC):
    TASK_ID = "base_task"

    def __init__(
        self,
    ):
        pass

    def execute(
        self,
        task_model: Any,
        task_inputs: List[Dict[str, Any]],
    ) -> Any:
        # TODO: iterate over task_inputs and execute the task
        # self._execute()
        # TODO: return the result of the task execution and merge it with the task_inputs
        pass

    @abstractmethod
    def _execute(
        self,
        task_input: Dict[str, Any],
    ):
        pass

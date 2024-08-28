from abc import ABC, abstractmethod
from typing import Any, Dict, List

from cyyrus.models.task_type import TaskType
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


class BaseTask(ABC):
    # The task ID is used to identify the task type
    TASK_ID = TaskType.DEFAULT

    # This flag indicates whether the task supports reference-free execution
    SUPPORTS_REFERENCE_FREE_EXECUTION = True

    def __init__(
        self,
        column_name: str,
        task_properties: Dict[str, Any],
    ) -> None:
        self.task_properties = task_properties
        self.column_name = column_name

    def reference_based_execution(
        self,
        task_input: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform a reference-based execution

        Strategy: Incase the task is reference-based, the task_input will be a dictionary containing the reference data. The final output will be a dictionary.
        """
        logger.debug(f"Executing reference based generation for task {self.TASK_ID} ...")
        interim_result = self.execute(
            task_input,
        )

        return {
            self.column_name: interim_result,
        }

    def reference_free_execution(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Perform a reference-free execution.

        Strategy: Incase the task is reference-free, the task_input will be None and the task will attempt to generate the reference data. The final output will be a list of dictionaries.
        """
        logger.debug(f"Executing reference free generation for task {self.TASK_ID} ...")

        if not self.SUPPORTS_REFERENCE_FREE_EXECUTION:
            logger.error(f"Skipping, Task {self.TASK_ID} does not support reference-free execution")
            return []

        task_inputs = self._generate_references()
        task_results = []
        for task_input in task_inputs:
            task_results.append(self.reference_based_execution(task_input))
        return task_results

    # The execute method is the main method that needs to be implemented by the task
    @abstractmethod
    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Perform the task execution
        """
        logger.debug(f"Executing task {self.TASK_ID} ...")
        return None

    # Incase the task supports reference-free execution, the task should implement the _generate_references method as well
    def _generate_references(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Attempt to generate the reference data for the task, using the task properties
        """
        return []

from typing import Any, Dict, List

from cyyrus.models.task_type import TaskType
from cyyrus.tasks.base import BaseTask
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


class DefaultTask(BaseTask):
    # The task ID is used to identify the task type
    TASK_ID = TaskType.DEFAULT

    # This flag indicates whether the task supports reference-free execution
    SUPPORTS_REFERENCE_FREE_EXECUTION = True

    # The execute method is the main method that needs to be implemented by the task
    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Perform the task execution
        """
        logger.debug(f"Executing default task with {self.TASK_ID} ...")
        return None

    # Incase the task supports reference-free execution, the task should implement the _generate_references method as well
    def _generate_references(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Attempt to generate the reference data for the task, using the task properties
        """
        logger.debug(f"Generating references for task {self.TASK_ID} ...")
        return []

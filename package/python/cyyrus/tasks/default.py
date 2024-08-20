from typing import Any, Dict

from cyyrus.models.task_type import TaskType
from cyyrus.tasks.base import BaseTask


class DefaultTask(BaseTask):
    TASK_ID = TaskType.DEFAULT

    def _execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        return f"Default Task: {task_input} with Task Properties: {self.task_properties}"

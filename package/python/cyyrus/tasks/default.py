from typing import Any, Dict

from cyyrus.tasks.base import BaseTask


class DefaultTask(BaseTask):
    TASK_ID = "default_task"

    def _execute(
        self,
        task_input: Dict[str, Any],
    ):
        pass

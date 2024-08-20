import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from cyyrus.models.task_type import TaskType


class BaseTask(ABC):
    TASK_ID = TaskType.DEFAULT

    def __init__(
        self,
        column_name: str,
        task_properties: Dict[str, Any],
    ) -> None:
        self.task_properties = task_properties
        self.column_name = column_name

    @staticmethod
    def flatten_dict(
        d: Dict[str, Any],
        parent_key: str = "",
        sep: str = "_",
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and max_depth > 1:
                items.extend(BaseTask.flatten_dict(v, new_key, sep, max_depth - 1).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        # Execute the task, and get the result
        try:
            result = self._execute(task_input)
        except Exception as e:
            warnings.warn(f"Error executing task {self.column_name}: {str(e)}")
            result = "Err"

        # If the result is a dictionary and the flatten property is set to True, flatten the dictionary
        if isinstance(result, dict) and self.task_properties.get("flatten", False):
            result = self.flatten_dict(result)

        # The final result should be a list of dictionaries, to be consistent with the output of all tasks and make it simpler to merge them into a dataframe
        return [
            {
                self.column_name: result,
            }
        ]

    @abstractmethod
    def _execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        return f"Default Task: {task_input} with Task Properties: {self.task_properties}"

import difflib
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

        if self._trigger_flattening():
            return self._flatten_dict(
                d=interim_result,
                parent_key=self.column_name,
            )
        else:
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

    # =====================================
    #           Utility methods
    # =====================================
    @staticmethod
    def _flatten_dict(
        d: Dict[str, Any],
        parent_key: str = "",
        sep: str = "_",
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        """
        Attempts to flatten the dictionary to a single level, by concatenating the keys with the separator. Upto the specified max_depth.
        """
        logger.debug(f"Attempting to flatten output with max_depth {max_depth} ...")
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and max_depth > 1:
                items.extend(BaseTask._flatten_dict(v, new_key, sep, max_depth - 1).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _get_task_property(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        The key used to extract the path from the task properties, incase the key is not found, the task will try to find the closest matching key
        """
        logger.debug(f"Fetching task property {key} ...")
        if key in list(self.task_properties.keys()):
            property_value = self.task_properties.get(
                key,
                default,
            )
        else:
            logger.debug("Key not found, attempting to find closest match ...")
            closest_key = self._find_closest_key(
                list(self.task_properties.keys()),
                key,
            )
            logger.debug(f"Closest key found: {closest_key}")
            property_value = self.task_properties.get(
                closest_key,
                default,
            )
        return property_value

    def _get_task_input(
        self,
        key: str,
        task_input: Dict[str, Any],
        default: Any = None,
    ) -> Any:
        """
        The key used to extract the path from the task input, incase the key is not found, the task will try to find the closest matching key
        """
        logger.debug(f"Fetching task input {key} ...")
        if key in list(task_input.keys()):
            property_value = task_input.get(
                key,
                default,
            )
        else:
            logger.debug("Key not found, attempting to find closest match ...")
            closest_key = self._find_closest_key(
                list(task_input.keys()),
                key,
            )

            logger.debug(f"Closest key found: {closest_key}")
            property_value = task_input.get(
                closest_key,
                default,
            )
        return property_value

    def _find_closest_key(
        self,
        keys: List[str],
        target: str,
    ) -> str:
        """
        Find the closest matching key from the list of keys.
        """
        if not keys:
            return ""
        return max(
            keys,
            key=lambda k: difflib.SequenceMatcher(
                None,
                k,
                target,
            ).ratio(),
        )

    def _trigger_flattening(
        self,
    ) -> bool:
        """
        Check if the task should trigger flattening
        """
        return self.task_properties.get(
            "flatten",
            False,
        )

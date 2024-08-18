from typing import Dict, Optional

from cyyrus.constants.messages import Messages
from cyyrus.errors.base import CyyrusException


class TaskNotFoundError(CyyrusException):
    """
    TaskNotFoundError class to handle task not found errors.
    """

    def __init__(
        self,
        message: str = Messages.REFERENCED_TASK_ID_NOT_FOUND,
        extra_info: Optional[Dict[str, str]] = None,  # Specify the task_id that was not found
    ):
        super().__init__(
            message,
            extra_info,
        )


class TaskPropertiesMissingError(CyyrusException):
    """
    TaskPropertiesMissingError class to handle task properties missing errors.
    """

    def __init__(
        self,
        message: str = Messages.TASK_PROPERTIES_UNSPECIFIED,
        extra_info: Optional[
            Dict[str, str]
        ] = None,  # Specify the task_id for which properties are missing
    ):
        super().__init__(
            message,
            extra_info,
        )


class TaskSpecificationMissingError(CyyrusException):
    """
    TaskSpecificationMissingError class to handle task specification missing errors.
    """

    def __init__(
        self,
        message: str = Messages.TASK_SPECIFICATION_MISSING,
        extra_info: Optional[
            Dict[str, str]
        ] = None,  # Specify the task_id for which specification is missing
    ):
        super().__init__(
            message,
            extra_info,
        )


class TaskCyclicDependencyError(CyyrusException):
    """
    TaskCyclicDependencyError class to handle task cyclic dependency errors.
    """

    def __init__(
        self,
        message: str = Messages.TASK_INPUTS_CYCLIC_DEPENDENCY,
        extra_info: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )

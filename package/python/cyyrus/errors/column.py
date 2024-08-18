from typing import Dict, Optional

from cyyrus.constants.messages import Messages

from .base import CyyrusException


class ColumnTypeNotFoundError(CyyrusException):
    """
    ColumnNotFoundError class to handle column not found errors.
    """

    def __init__(
        self,
        message: str = Messages.COLUMN_TYPE_NOT_FOUND,
        extra_info: Optional[Dict[str, str]] = None,  # Specify the column_id that was not found
    ):
        super().__init__(
            message,
            extra_info,
        )


class ColumnIDNotFoundError(CyyrusException):
    """
    ColumnIDNotFoundError class to handle column id not found errors.
    """

    def __init__(
        self,
        message: str = Messages.COLUMNN_ID_NOT_FOUND,
        extra_info: Optional[Dict[str, str]] = None,  # Specify the column_id that was not found
    ):
        super().__init__(
            message,
            extra_info,
        )


class ColumnTaskIDNotFoundError(CyyrusException):
    """
    ColumnTaskIDNotFoundError class to handle column task_id not found errors.
    """

    def __init__(
        self,
        message: str = Messages.COLUMN_TASK_ID_NOT_FOUND,
        extra_info: Optional[
            Dict[str, str]
        ] = None,  # Specify the column_id for which task_id is missing
    ):
        super().__init__(
            message,
            extra_info,
        )


class DuplicateColumnIDError(CyyrusException):
    """
    DuplicateColumnIDError class to handle duplicate column id errors.
    """

    def __init__(
        self,
        message: str = Messages.DUPLICATE_COLUMN_NAME,
        extra_info: Optional[Dict[str, str]] = None,  # Specify the column_id that is duplicated
    ):
        super().__init__(
            message,
            extra_info,
        )
        super().__init__(message)

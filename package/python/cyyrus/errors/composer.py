from typing import Any, Dict, Optional

from cyyrus.constants.messages import Messages
from cyyrus.errors.base import CyyrusException, CyyrusWarning


class KeyColumnNotFoundError(CyyrusException):
    """
    KeyColumnNotFoundError class to handle key column not found errors.
    """

    def __init__(
        self,
        message: str = Messages.KEY_COLUMN_NOT_FOUND,
        extra_info: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class InvalidKeyColumnError(CyyrusException):
    """
    InvalidKeyColumnError class to handle invalid key column errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_KEY_COLUMN,
        extra_info: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class AllRowsExcludedDueToNanWarning(CyyrusWarning):
    """
    AllRowsExcludedDueToNanWarning class to handle all rows excluded due to NaN warnings.
    """

    def __init__(self, message: str = Messages.ALL_ROWS_EXCLUDED_DUE_TO_NAN):
        super().__init__(message)


class RequiredColumnMissingWarning(CyyrusWarning):
    """
    RequiredColumnMissingWarning class to handle required column missing warnings.
    """

    def __init__(
        self,
        message: str = Messages.REQUIRED_COLUMN_MISSING,
        extra_info: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class NonUniqueColumnValuesWarning(CyyrusWarning):
    """
    NonUniqueColumnValuesWarning class to handle non-unique column values warnings.
    """

    def __init__(
        self,
        message: str = Messages.NON_UNIQUE_COLUMN_VALUES,
        extra_info: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class DatasetTooSmallForSplitWarning(CyyrusWarning):
    """
    DatasetTooSmallWarning class to handle dataset too small warnings.
    """

    def __init__(
        self,
        message: str = Messages.DATASET_TOO_SMALL_FOR_SPLIT,
        extra_info: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class ReAdjustingSplitWarning(CyyrusWarning):
    """
    ReAdjustingSplitWarning class to handle re-adjusting split warnings.
    """

    def __init__(
        self,
        message: str = Messages.RE_ADJUSTING_SPLIT,
        extra_info: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )

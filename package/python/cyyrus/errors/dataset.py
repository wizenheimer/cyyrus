from typing import Any, Dict, Optional

from cyyrus.constants.messages import Messages
from cyyrus.errors.base import CyyrusWarning

# ==============================
# Warnings for Dataset Section
# ==============================


class SplitsDontAddUpWarning(CyyrusWarning):
    """
    SplitsDontAddUpWarning class to handle dataset splits don't add up errors.
    """

    def __init__(
        self,
        message: str = Messages.SPLITS_DONT_ADD_UP,
        extra_info: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class SplitValueInvalidWarning(CyyrusWarning):
    """
    SplitValueInvalidWarning class to handle dataset split value negative or zero errors.
    """

    def __init__(
        self,
        message: str = Messages.SPLIT_VALUE_INVALID,
        extra_info: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class InvalidNullHandlingStrategyWarning(CyyrusWarning):
    """
    InvalidNullHandlingStrategyWarning class to handle dataset invalid null handling strategy errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_NULL_HANDLING_STRATEGY,
        extra_info: Optional[Dict[str, str]] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class InvalidShufflingStrategyWarning(CyyrusWarning):
    """
    InvalidShufflingStrategyWarning class to handle dataset invalid shuffling strategy errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_SHUFFLING_STRATEGY,
        extra_info: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )

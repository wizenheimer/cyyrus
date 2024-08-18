from typing import Dict, Optional

from cyyrus.constants.messages import Messages
from cyyrus.errors.base import CyyrusException, CyyrusWarning


class TypePropertiesMissingForObjectError(CyyrusException):
    """
    TypePropertiesMissingForObjectError class to handle type properties missing for object errors.
    """

    def __init__(self, message: str = Messages.TYPE_PROPERTIES_MISSING_FOR_OBJECT_TYPE):
        super().__init__(message)


class TypeItemsMissingForArrayError(CyyrusException):
    """
    TypeItemsMissingForArrayError class to handle type items missing for array errors.
    """

    def __init__(self, message: str = Messages.TYPE_ITEMS_MISSING_FOR_ARRAY_TYPE):
        super().__init__(message)


class DuplicateTypeNameError(CyyrusException):
    """
    DuplicateTypeNameError class to handle duplicate type name errors.
    """

    def __init__(self, message: str = Messages.DUPLICATE_TYPE_NAME):
        super().__init__(message)


class ReferenceTypeNotFoundError(CyyrusWarning):
    """
    ReferenceTypeNotFoundError class to handle reference type not found errors.
    """

    def __init__(self, message: str = Messages.REFERENCE_TYPE_NOT_FOUND):
        super().__init__(message)


class InvalidTypeError(CyyrusException):
    """
    InvalidTypeError class to handle invalid base type errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_TYPE,
        extra_info: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class MaximumDepthExceededError(CyyrusException):
    """
    MaximumDepthExceededError class to handle maximum depth exceeded errors.
    """

    def __init__(
        self,
        message: str = Messages.MAXIMUM_DEPTH_EXCEEDED,
        extra_info: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )

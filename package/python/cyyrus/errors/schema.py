from typing import Dict, Optional

from cyyrus.constants.messages import Messages

from .base import CyyrusException

# ==============================
# Schema Section validation errors
# ==============================


class SchemaValidationError(CyyrusException):
    """
    SchemaValidationError class to handle schema validation errors.
    """

    def __init__(self, message: str = Messages.SCHEMA_COULD_NOT_BE_VALIDATED):
        super().__init__(message)


class SchemaParsingError(CyyrusException):
    """
    SchemaParsingError class to handle schema parsing errors.
    """

    def __init__(
        self,
        message: str = Messages.SCHEMA_COULD_NOT_BE_PARSED,
        extra_info: Optional[Dict[str, str]] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class SchemaFileNotFoundError(CyyrusException):
    """
    SchemaFileNotFoundError class to handle schema file not found errors.
    """

    def __init__(
        self,
        message: str = Messages.SCHEMA_FILE_COULD_NOT_BE_LOCATED,
        extra_info: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class SchemaRequiredSectionMissingError(CyyrusException):
    """
    SchemaRequiredSectionMissingError class to handle schema required section missing errors.
    """

    def __init__(self, message: str = Messages.REQUIRED_SECTION_MISSING_IN_SCHEMA):
        super().__init__(message)

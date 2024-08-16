from typing import Dict
from cyyrus.constants.messages import Messages
from .base import CyyrusException, CyyrusWarning

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
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class SchemaFileNotFoundError(CyyrusException):
    """
    SchemaFileNotFoundError class to handle schema file not found errors.
    """

    def __init__(self, message: str = Messages.SCHEMA_FILE_COULD_NOT_BE_LOCATED):
        super().__init__(message)


class SchemaRequiredSectionMissingError(CyyrusException):
    """
    SchemaRequiredSectionMissingError class to handle schema required section missing errors.
    """

    def __init__(self, message: str = Messages.REQUIRED_SECTION_MISSING_IN_SCHEMA):
        super().__init__(message)


# ==============================
# Reference Section validation error
# ==============================


class ReferenceTypeMissingError(CyyrusException):
    """
    ReferenceTypeMissingError class to handle reference type missing errors.
    """

    def __init__(
        self,
        message: str = Messages.REFERENCE_TYPE_MISSING,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class ReferenceTypeNotSupportedError(CyyrusException):
    """
    ReferenceTypeNotSupportedError class to handle reference type not supported errors.
    """

    def __init__(
        self,
        message: str = Messages.REFERENCE_TYPE_NOT_SUPPORTED,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class ReferencePropertiesMissingError(CyyrusException):
    """
    ReferencePropertiesMissingError class to handle reference properties missing errors.
    """

    def __init__(
        self,
        message: str = Messages.REFERENCE_PROPERTIES_MISSING,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class ReferencePropertiesInvalidError(CyyrusException):
    """
    ReferencePropertiesInvalidError class to handle reference properties invalid errors.
    """

    def __init__(self, message: str = Messages.REFERENCE_PROPERTIES_INVALID):
        super().__init__(message)


# ==============================
# Dataset Section validation error
# ==============================


class DatasetSplitsDontAddUpError(CyyrusWarning):
    """
    DatasetSplitsDontAddUpError class to handle dataset splits don't add up errors.
    """

    def __init__(
        self,
        message: str = Messages.SPLITS_DONT_ADD_UP,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class DatasetInvalidTagTypesError(CyyrusWarning):
    """
    DatasetInvalidTagTypesError class to handle dataset invalid tag types errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_TAG_TYPES,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class DatasetInvalidSamplingStrategyError(CyyrusWarning):
    """
    DatasetInvalidSamplingStrategyError class to handle dataset invalid sampling strategy errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_SAMPLING_STRATEGY,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class DatasetInvalidNullHandlingStrategyError(CyyrusWarning):
    """
    DatasetInvalidNullHandlingStrategyError class to handle dataset invalid null handling strategy errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_NULL_HANDLING_STRATEGY,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(message, extra_info=extra_info)


class DatasetInvalidReferenceHandlingStrategyError(CyyrusWarning):
    """
    DatasetInvalidReferenceHandlingStrategyError class to handle dataset invalid reference handling strategy errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_REFERENCE_HANDLING_STRATEGY,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class DatasetInvalidShufflingStrategyError(CyyrusWarning):
    """
    DatasetInvalidShufflingStrategyError class to handle dataset invalid shuffling strategy errors.
    """

    def __init__(
        self,
        message: str = Messages.INVALID_SHUFFLING_STRATEGY,
        extra_info: Dict[str, str] = None,
    ):
        super().__init__(
            message,
            extra_info=extra_info,
        )


class DatasetInvalidSplitValueError(CyyrusException):
    """
    DatasetInvalidSplitValueError class to handle dataset invalid split value errors.
    """

    def __init__(self, message: str = Messages.INVALID_SPLIT_VALUE):
        super().__init__(message)


# ==============================
# Types Section validation error
# ==============================


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


class InvalidBaseTypeError(CyyrusWarning):
    """
    InvalidBaseTypeError class to handle invalid base type errors.
    """

    def __init__(self, message: str = Messages.INVALID_BASE_TYPE):
        super().__init__(message)


# ==============================
# Task Section validation error
# ==============================


class TaskNotFoundError(CyyrusException):
    """
    TaskNotFoundError class to handle task not found errors.
    """

    def __init__(
        self,
        message: str = Messages.REFERENCED_TASK_ID_NOT_FOUND,
        extra_info: Dict[str, str] = None,  # Specify the task_id that was not found
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
        extra_info: Dict[str, str] = None,  # Specify the task_id for which properties are missing
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
        extra_info: Dict[str, str] = None,  # Specify the task_id for which specification is missing
    ):
        super().__init__(
            message,
            extra_info,
        )


# ==============================
# Column Section validation error
# ==============================


class ColumnTypeNotFoundError(CyyrusException):
    """
    ColumnNotFoundError class to handle column not found errors.
    """

    def __init__(
        self,
        message: str = Messages.COLUMN_TYPE_NOT_FOUND,
        extra_info: Dict[str, str] = None,  # Specify the column_id that was not found
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
        extra_info: Dict[str, str] = None,  # Specify the column_id that was not found
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
        extra_info: Dict[str, str] = None,  # Specify the column_id for which task_id is missing
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
        extra_info: Dict[str, str] = None,  # Specify the column_id that is duplicated
    ):
        super().__init__(
            message,
            extra_info,
        )
        super().__init__(message)

import re
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    create_model,
)
from pydantic.fields import Field
from pydantic.functional_validators import model_validator

from cyyrus.constants.messages import Messages
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


class DataType(str, Enum):
    """
    Enum for the different data types supported by the API.
    """

    DEFAULT = "string"
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ObjectProperty(BaseModel):
    """
    Pydantic model for defining an object property.
    """

    type: DataType


class ArrayItems(BaseModel):
    """
    Pydantic model for defining the items in an array.
    """

    type: DataType
    properties: Optional[Dict[str, Union[ObjectProperty, str]]] = None

    @model_validator(mode="after")
    def validate_properties(cls, values):
        logger.debug(f"Validating properties for {cls}")
        if values.properties:
            for key, value in values.properties.items():
                if isinstance(value, str):
                    values.properties[key] = ObjectProperty(
                        type=DataType(value),
                    )
        logger.debug(f"Properties after validation: {values.properties}")
        return values


class CustomType(BaseModel):
    type: DataType
    properties: Optional[
        Dict[
            str,
            Union[
                str,
                ObjectProperty,
                Dict[str, Any],
            ],
        ]
    ] = None
    items: Optional[ArrayItems] = None

    @model_validator(mode="after")
    def validate_properties(cls, values):
        logger.debug(f"Validating properties for {cls}")
        if values.properties:
            for key, value in values.properties.items():
                if isinstance(value, str):
                    values.properties[key] = ObjectProperty(type=value)  # type: ignore
        logger.debug(f"Properties after validation: {values.properties}")
        return values

    @model_validator(mode="after")
    def validate_items(cls, values):
        logger.debug(f"Validating items for {cls}")
        if values.items and isinstance(values.items, dict):
            values.items = ArrayItems(**values.items)
        logger.debug(f"Items after validation: {values.items}")
        return values


# ================================================================================================
#                                   Type Mapping Functions
# These functions take task and type definitions and return the appropriate type as pydantic model
# ================================================================================================


class DefaultModel(BaseModel):
    """
    Pydantic model for the default data type.
    """

    value: str = Field(..., description="value")


class MarkdownModel(BaseModel):
    """
    Pydantic model representing the structure and content of a Markdown file.
    """

    markdown: str = Field(..., description="Markdown content")


class TypeMappingUtils:
    """
    Utility class for mapping task and type definitions to a concrete pydantic models.
    """

    @staticmethod
    def sanitize_name(name: str) -> str:
        """
        Sanitize the given name to ensure it only contains valid characters.
        """
        # Replace any non-alphanumeric characters with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9]", "_", name)
        # Ensure the name starts with a letter
        if not sanitized[0].isalpha():
            sanitized = "Model_" + sanitized
        return sanitized

    @staticmethod
    def get_python_type(
        type_string: str,
    ) -> type:
        """
        Get the python type corresponding to the given type string.
        """

        TYPE_MAPPING = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool,
        }

        return TYPE_MAPPING.get(
            type_string.lower(),
            Any,
        )

    @staticmethod
    def get_concrete_model(
        type_def: Optional[Dict[str, Any]] = None,
        depth: int = 0,
        max_depth: int = 5,
    ) -> type[BaseModel]:
        """
        Get the concrete pydantic model for the given type definition.
        """

        if type_def is None:
            logger.debug("Type definition is None, using default model")
            return DefaultModel

        # Check if the depth exceeds the maximum depth
        if depth >= max_depth:
            logger.error(f"{Messages.MAXIMUM_DEPTH_EXCEEDED}")
            logger.debug(f"Max depth: {max_depth}, Current depth: {depth}")
            raise ValueError(Messages.MAXIMUM_DEPTH_EXCEEDED)

        # Get the type value from the type definition
        type_value = type_def["type"]

        logger.debug(f"Creating model for type value: {type_value}")

        # Recursively create models for nested types
        if type_value == "object":
            logger.debug("Creating model for object type")
            model_name = TypeMappingUtils.sanitize_name(f"ObjectModel_{depth}")

            fields = {}

            # Iterate over the properties and create models for each property
            for prop_name, prop_type in type_def.get(
                "properties",
                {},
            ).items():
                # If the property type is a dictionary, create a model for it
                if isinstance(prop_type, dict):
                    fields[prop_name] = (
                        TypeMappingUtils.get_concrete_model(
                            prop_type,
                            depth + 1,
                            max_depth,
                        ),
                        ...,
                    )
                else:
                    fields[prop_name] = (
                        TypeMappingUtils.get_python_type(
                            prop_type,
                        ),
                        ...,
                    )
            return create_model(
                model_name,
                **fields,
            )
        # If the type is an array, create a model for the items
        elif type_value == "array":
            logger.debug("Creating model for array type")
            model_name = TypeMappingUtils.sanitize_name(f"ArrayModel_{depth}")

            item_type = TypeMappingUtils.get_concrete_model(
                type_def["items"],
                depth + 1,
                max_depth,
            )
            return create_model(
                model_name,
                items=(
                    List[item_type],
                    ...,
                ),
            )
        # If the type is a primitive type, return the corresponding python type
        else:
            logger.debug("Creating model for primitive type")
            model_name = TypeMappingUtils.sanitize_name(f"{type_value.capitalize()}Model_{depth}")

            python_type = TypeMappingUtils.get_python_type(
                type_value,
            )
            return create_model(
                model_name,
                value=(python_type, ...),
            )

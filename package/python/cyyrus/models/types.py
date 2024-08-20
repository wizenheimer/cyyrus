from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    create_model,
)
from pydantic.fields import Field
from pydantic.functional_validators import model_validator

from cyyrus.errors.types import MaximumDepthExceededError


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
        if values.properties:
            for key, value in values.properties.items():
                if isinstance(value, str):
                    values.properties[key] = ObjectProperty(
                        type=DataType(value),
                    )
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
        if values.properties:
            for key, value in values.properties.items():
                if isinstance(value, str):
                    values.properties[key] = ObjectProperty(type=value)  # type: ignore
        return values

    @model_validator(mode="after")
    def validate_items(cls, values):
        if values.items and isinstance(values.items, dict):
            values.items = ArrayItems(**values.items)
        return values


# ================================================================================================
#                                   Type Mapping Functions
# These functions take task and type definitions and return the appropriate type as pydantic model
# ================================================================================================


class DefaultModel(BaseModel):
    """
    Pydantic model for the default data type.
    """

    result: str = Field(..., description="result")


class TypeMappingUtils:
    """
    Utility class for mapping task and type definitions to a concrete pydantic models.
    """

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
            return DefaultModel

        # Check if the depth exceeds the maximum depth
        if depth >= max_depth:
            raise MaximumDepthExceededError(
                extra_info={
                    "max_depth": str(max_depth),
                },
            )

        # Get the type value from the type definition
        type_value = type_def["type"]

        # Recursively create models for nested types
        if type_value == "object":
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
                f"DynamicModel_{depth}",
                **fields,
            )
        # If the type is an array, create a model for the items
        elif type_value == "array":
            item_type = TypeMappingUtils.get_concrete_model(
                type_def["items"],
                depth + 1,
                max_depth,
            )
            return create_model(
                f"ArrayModel_{depth}",
                items=(
                    List[item_type],
                    ...,
                ),
            )
        # If the type is a primitive type, return the corresponding python type
        else:
            python_type = TypeMappingUtils.get_python_type(
                type_value,
            )
            return create_model(
                f"PrimitiveModel_{type_def['type']}_{depth}",
                value=(python_type, ...),
            )

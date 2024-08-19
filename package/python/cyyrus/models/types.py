from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union

from pydantic import (
    BaseModel,
    create_model,
)
from pydantic.fields import Field
from pydantic.functional_validators import model_validator

from cyyrus.errors.types import MaximumDepthExceededError
from cyyrus.models.task import TaskType

# =============================================================================
#                               Supported Datatypes
# =============================================================================


class DataType(str, Enum):
    DEFAULT = "string"
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


# =============================================================================
#                              Static Types
#     These are for tasks which have predefined types for their outputs
# =============================================================================


class StaticStringModel(BaseModel):
    value: str = Field(
        ...,
        description="Value of the type",
    )


class StaticIntegerModel(BaseModel):
    value: int = Field(
        ...,
        description="Value of the type",
    )


class StaticFloatModel(BaseModel):
    value: float = Field(
        ...,
        description="Value of the type",
    )


class StaticBooleanModel(BaseModel):
    value: bool = Field(
        ...,
        description="Value of the type",
    )


class StaticArrayModel(BaseModel):
    value: List[Union[str, int, float, bool]] = Field(
        ...,
        description="Items of the array",
    )


# =============================================================================
#                             Dynamic Types
#    These are for tasks which have dynamic types for their outputs
# =============================================================================


class ObjectProperty(BaseModel):
    type: DataType


class ArrayItems(BaseModel):
    type: DataType
    properties: Optional[Dict[str, Union[ObjectProperty, str]]] = None

    @model_validator(mode="after")
    def validate_properties(cls, values):
        if values.properties:
            for key, value in values.properties.items():
                if isinstance(value, str):
                    values.properties[key] = ObjectProperty(type=value)  # type: ignore
        return values


# =============================================================================
#                             Custom Type for Spec
# =============================================================================


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


DYNAMIC_TASKS: Set[TaskType] = {
    TaskType.GENERATION,
}


def get_types(
    task_type: TaskType,
    type_def: Dict[str, Any],
) -> type[
    BaseModel
    | StaticIntegerModel
    | StaticFloatModel
    | StaticBooleanModel
    | StaticArrayModel
    | StaticStringModel
]:
    if task_type in DYNAMIC_TASKS:
        # If the task type is in custom_typed, then we need to create a dynamic type as per the type_def
        return get_dynamic_model(type_def)
    else:
        # If the task type is not in custom_typed, then we disregard the type_def and create a static type
        return get_static_model(task_type)


def get_static_model(
    task_type: TaskType,
) -> type[
    BaseModel
    | StaticIntegerModel
    | StaticFloatModel
    | StaticBooleanModel
    | StaticArrayModel
    | StaticStringModel
]:
    TASK_TO_TYPE_MAPPING: Dict[TaskType, Type[BaseModel]] = {
        TaskType.EMBEDDING: StaticArrayModel,
    }

    return TASK_TO_TYPE_MAPPING.get(task_type, StaticStringModel)


def get_python_type(
    type_string: str,
) -> type:
    TYPE_MAPPING = {
        "string": str,
        "integer": int,
        "float": float,
        "boolean": bool,
    }

    return TYPE_MAPPING.get(type_string.lower(), Any)


def get_dynamic_model(
    type_def: Dict[str, Any],
    depth: int = 0,
    max_depth: int = 5,
) -> type[BaseModel]:
    if depth >= max_depth:
        raise MaximumDepthExceededError(
            extra_info={
                "max_depth": str(max_depth),
            },
        )

    type_value = type_def["type"]
    # Recursively create models for nested types
    if type_value == "object":
        fields = {}
        for prop_name, prop_type in type_def.get("properties", {}).items():
            if isinstance(prop_type, dict):
                fields[prop_name] = (
                    get_dynamic_model(
                        prop_type,
                        depth + 1,
                        max_depth,
                    ),
                    ...,
                )
            else:
                fields[prop_name] = (
                    get_python_type(
                        prop_type,
                    ),
                    ...,
                )
        return create_model(
            f"DynamicModel_{depth}",
            **fields,
        )
    elif type_value == "array":
        item_type = get_dynamic_model(
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
    else:
        python_type = get_python_type(
            type_value,
        )
        return create_model(
            f"PrimitiveModel_{type_def['type']}_{depth}",
            value=(python_type, ...),
        )

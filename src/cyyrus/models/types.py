from pydantic import (
    BaseModel,
    create_model,
)
from pydantic.functional_validators import model_validator
from typing import Any, Dict, Union, Optional, List
from enum import Enum
from cyyrus.errors.schema import InvalidTypeError, MaximumDepthExceededError


class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ObjectProperty(BaseModel):
    type: DataType  # Union[DataType, str] incase, we allow aliasing


class ArrayItems(BaseModel):
    type: DataType  # Union[DataType, str] incase, we allow aliasing
    properties: Optional[Dict[str, Union[ObjectProperty, str]]] = None

    @model_validator(mode="after")
    def validate_properties(cls, values):
        if values.properties:
            for key, value in values.properties.items():
                if isinstance(value, str):
                    values.properties[key] = ObjectProperty(type=value)  # type: ignore
        return values


class Type(BaseModel):
    type: DataType  # Union[DataType, str] incase, we allow aliasing
    properties: Optional[Dict[str, Union[str, ObjectProperty, Dict[str, Any]]]] = None
    items: Optional[ArrayItems] = None
    dynamic_model: Optional[Any] = None

    def __init__(self, **data):
        super().__init__(**data)
        try:
            self.dynamic_model = create_dynamic_type(
                self.model_dump(
                    exclude={"dynamic_model"},
                )
            )
        except Exception as e:
            raise InvalidTypeError(extra_info={"error": str(e)})

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


def get_python_type(type_string: str) -> type:
    TYPE_MAPPING = {
        "string": str,
        "integer": int,
        "float": float,
        "boolean": bool,
    }
    return TYPE_MAPPING.get(type_string.lower(), Any)


def create_dynamic_type(
    type_def: Dict[str, Any], depth: int = 0, max_depth: int = 5
) -> Union[type, BaseModel]:
    if depth >= max_depth:
        raise MaximumDepthExceededError(extra_info={"max_depth": str(max_depth)})

    # Recursively create models for nested types
    if type_def["type"] == "object":
        fields = {}
        for prop_name, prop_type in type_def.get("properties", {}).items():
            if isinstance(prop_type, dict):
                fields[prop_name] = (create_dynamic_type(prop_type, depth + 1, max_depth), ...)
            else:
                fields[prop_name] = (get_python_type(prop_type), ...)
        return create_model("DynamicModel", **fields)
    elif type_def["type"] == "array":
        item_type = create_dynamic_type(type_def["items"], depth + 1, max_depth)
        return List[item_type]
    else:
        return get_python_type(type_def["type"])

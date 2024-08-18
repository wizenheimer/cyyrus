from pydantic import (
    BaseModel,
    create_model,
)
from pydantic.fields import Field
from pydantic.functional_validators import model_validator
from typing import Any, Dict, Union, Optional, List, Type
from enum import Enum

from cyyrus.errors.schema import InvalidTypeError, MaximumDepthExceededError


class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    IMAGE = "image"
    AUDIO = "audio"


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


class CustomType(BaseModel):
    type: DataType  # Union[DataType, str] incase, we allow aliasing
    properties: Optional[Dict[str, Union[str, ObjectProperty, Dict[str, Any]]]] = None
    items: Optional[ArrayItems] = None
    dynamic_model: Optional[Any] = Field(None, exclude=True)

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


def get_binary_type(type_string: str) -> type:
    TYPE_MAPPING = {
        "image": str,  # image and audio files are base64 encoded strings
        "audio": str,
    }
    return TYPE_MAPPING.get(type_string.lower(), Any)  # type: ignore


def create_dynamic_type(
    type_def: Dict[str, Any], depth: int = 0, max_depth: int = 5
) -> type[BaseModel]:
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
        return create_model(f"DynamicModel_{depth}", **fields)
    elif type_def["type"] == "array":
        item_type = create_dynamic_type(type_def["items"], depth + 1, max_depth)
        return create_model(f"ArrayModel_{depth}", items=(List[item_type], ...))
    elif type_def["type"] in ["image", "audio"]:
        python_type = get_binary_type(type_def["type"])
        return create_model(f"FileModel_{type_def['type']}_{depth}", value=(python_type, ...))
    else:
        python_type = get_python_type(type_def["type"])
        return create_model(f"PrimitiveModel_{type_def['type']}_{depth}", value=(python_type, ...))


def create_nested_model(
    models: Dict[str, Type[BaseModel]],
    new_model_name: str = "NestedModel",
) -> Type[BaseModel]:
    """
    Create a new Pydantic model that nests the given models as fields.

    :param models: A list of Pydantic model classes to be nested
    :param new_model_name: The name for the new model (default: "NestedModel")
    :return: A new Pydantic model class with nested fields
    """
    field_definitions = {model_name: (model, ...) for model_name, model in models.items()}

    return create_model(new_model_name, **field_definitions)  # type: ignore


def unnest_model(
    nested_instance: BaseModel,
    models: Dict[str, Type[BaseModel]],
) -> Dict[str, BaseModel]:
    """
    Take an instance of a nested model and a list of model classes,
    and return instances of those individual models.

    :param nested_instance: An instance of a nested Pydantic model
    :param models: A list of Pydantic model classes to unnest
    :return: A dictionary of unnested model instances
    """
    unnested = {}
    for model_name in models.keys():
        field_name = model_name
        if hasattr(nested_instance, field_name):
            unnested[field_name] = getattr(nested_instance, field_name).dict()
    return unnested

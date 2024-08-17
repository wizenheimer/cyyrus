from pydantic import (
    BaseModel,
    create_model,
)
from pydantic.fields import Field, FieldInfo
from pydantic.functional_validators import model_validator
from typing import Any, Dict, Union, Optional, List, Type, get_origin, get_args
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


def merge_pydantic_models(
    models: List[Union[Type[BaseModel], type, str, CustomType]],
    model_name: str = "MergedModel",
) -> Type[BaseModel]:
    """
    Merge multiple Pydantic models and/or Python types into a single model.

    :param models: List of Pydantic model classes, Python types, type strings, or CustomType to merge
    :param model_name: Name of the resulting merged model (default is "MergedModel")
    :return: A tuple containing the new Pydantic model class and the list of original models
    """
    merged_fields = {}
    for model in models:
        if isinstance(model, Type) and issubclass(model, BaseModel):
            # It's a Pydantic model
            merged_fields.update(model.model_fields)
        elif isinstance(model, (type, CustomType)):
            # It's a Python type or CustomType
            field_name = model.__name__.lower()
            merged_fields[field_name] = FieldInfo(annotation=model)  # type: ignore
        elif isinstance(model, str):
            # It's a type string
            python_type = get_python_type(model)
            field_name = model.lower()
            merged_fields[field_name] = FieldInfo(annotation=python_type)
        elif get_origin(model) is not None:
            # It's a generic type (e.g., List[...])
            origin = get_origin(model)
            _ = get_args(model)
            field_name = origin.__name__.lower()
            merged_fields[field_name] = FieldInfo(annotation=model)
        else:
            raise ValueError(f"Unsupported model type: {type(model)}")

    return create_model(
        model_name,
        **{field_name: (field.annotation, field) for field_name, field in merged_fields.items()},  # type: ignore
    )  # type: ignore


def split_merged_model(
    merged_instance: BaseModel,
    original_models: List[Union[Type[BaseModel], CustomType, str]],
):
    """
    Split a merged model instance back into instances of the original models or values of original types.

    :param merged_instance: An instance of the merged model
    :param original_models: List of original models/types used to create the merged model
    :return: A dictionary mapping original models/types to their respective instances/values
    """
    result = {}
    merged_dict = merged_instance.model_dump()

    for model in original_models:
        if isinstance(model, type) and issubclass(model, BaseModel):
            # It's a Pydantic model
            field_dict = {
                field: merged_dict[field] for field in model.model_fields if field in merged_dict
            }
            result[model] = model(**field_dict)
        elif isinstance(model, type):
            # It's a Python type
            field_name = model.__name__.lower()
            if field_name in merged_dict:
                result[model] = merged_dict[field_name]
        elif isinstance(model, str):
            # It's a type string
            field_name = model.lower()
            if field_name in merged_dict:
                result[model] = merged_dict[field_name]
        elif get_origin(model) is not None:
            # It's a generic type (e.g., List[...])
            origin = get_origin(model)
            args = get_args(model)
            if origin is None:
                field_name = model.__name__.lower()
            else:
                field_name = origin.__name__.lower()
            if field_name in merged_dict:
                # If it's a List of Pydantic models, we need to instantiate each item
                if (
                    origin is list
                    and args
                    and isinstance(args[0], type)
                    and issubclass(args[0], BaseModel)
                ):
                    result[model] = [args[0](**item) for item in merged_dict[field_name]]
                else:
                    result[model] = merged_dict[field_name]
        else:
            raise ValueError(f"Unsupported model type: {type(model)}")

    return result

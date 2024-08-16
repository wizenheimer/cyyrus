from pydantic import BaseModel, model_validator
from typing import Dict, Union, Optional
from enum import Enum


class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ObjectProperty(BaseModel):
    type: Union[DataType, str]


class ArrayItems(BaseModel):
    type: Union[DataType, str]
    properties: Optional[Dict[str, Union[ObjectProperty, str]]] = None

    @model_validator(mode="after")
    def validate_properties(cls, values):
        if values.properties:
            for key, value in values.properties.items():
                if isinstance(value, str):
                    values.properties[key] = ObjectProperty(type=value)
        return values


class Type(BaseModel):
    type: Union[DataType, str]
    properties: Optional[Dict[str, Union[ObjectProperty, str]]] = None
    items: Optional[ArrayItems] = None

    @model_validator(mode="after")
    def validate_properties(cls, values):
        if values.properties:
            for key, value in values.properties.items():
                if isinstance(value, str):
                    values.properties[key] = ObjectProperty(type=value)
        return values

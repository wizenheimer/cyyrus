from typing import get_args, get_origin

import pytest
from cyyrus.errors.types import MaximumDepthExceededError  # type: ignore
from cyyrus.models.types import (  # type: ignore
    ArrayItems,
    CustomType,
    DataType,
    ObjectProperty,
    get_dynamic_model,
)
from pydantic import BaseModel, ValidationError


@pytest.mark.xfail(reason="Alias types are not supported in the schema for v0")
def test_alias_types():
    # Test with custom string type
    items2 = ArrayItems(type="custom_type")  # type: ignore
    assert items2.type == "custom_type"
    assert items2.properties is None

    # Test with custom string type
    prop2 = ObjectProperty(type="custom_type")  # type: ignore
    assert prop2.type == "custom_type"

    # Test with invalid type
    CustomType(type="invalid_type")


def test_array_items():
    # Test valid ArrayItems
    valid_items = ArrayItems(type=DataType.STRING)
    assert valid_items.type == DataType.STRING
    assert valid_items.properties is None

    # Test with DataType
    items1 = ArrayItems(type=DataType.INTEGER)
    assert items1.type == DataType.INTEGER
    assert items1.properties is None

    # Test with properties
    items3 = ArrayItems(
        type=DataType.OBJECT,
        properties={"prop1": ObjectProperty(type=DataType.STRING), "prop2": "integer"},
    )
    assert items3.type == DataType.OBJECT
    assert items3.properties["prop1"].type == DataType.STRING  # type: ignore
    assert items3.properties["prop2"].type == "integer"  # type: ignore

    # Test ArrayItems with properties
    items_with_props = ArrayItems(
        type=DataType.OBJECT, properties={"prop1": ObjectProperty(type=DataType.INTEGER)}
    )
    assert items_with_props.type == DataType.OBJECT
    assert "prop1" in items_with_props.properties  # type: ignore
    assert items_with_props.properties["prop1"].type == DataType.INTEGER  # type: ignore

    # Test ArrayItems with string property
    items_with_string_prop = ArrayItems(type=DataType.OBJECT, properties={"prop1": "string"})
    assert items_with_string_prop.properties["prop1"].type == "string"  # type: ignore

    # Test with invalid type
    with pytest.raises(ValidationError):
        ArrayItems(type=123)  # type: ignore

    # Test with invalid properties
    with pytest.raises(ValidationError):
        ArrayItems(type=DataType.OBJECT, properties={"prop1": 123})  # type: ignore


def test_type():
    # Test valid Type
    valid_type = CustomType(type=DataType.STRING)
    assert valid_type.type == DataType.STRING
    assert valid_type.properties is None
    assert valid_type.items is None

    # Test Type with properties
    type_with_props = CustomType(
        type=DataType.OBJECT, properties={"prop1": ObjectProperty(type=DataType.INTEGER)}
    )
    assert type_with_props.type == DataType.OBJECT
    assert "prop1" in type_with_props.properties  # type: ignore
    assert type_with_props.properties["prop1"].type == DataType.INTEGER  # type: ignore

    # Test Type with items
    type_with_items = CustomType(type=DataType.ARRAY, items=ArrayItems(type=DataType.STRING))
    assert type_with_items.type == DataType.ARRAY
    assert type_with_items.items.type == DataType.STRING  # type: ignore

    # Test invalid Type (missing required field)
    with pytest.raises(ValidationError):
        CustomType()

    # Test Type with invalid dynamic model
    with pytest.raises(ValidationError):
        CustomType(
            type="invalid_type"
        )  # Deviates from the schema, which doesn't allow custom/aliased types


def test_create_dynamic_type():
    # Test primitive types
    str_model = get_dynamic_model({"type": "string"})
    assert issubclass(str_model, BaseModel)
    assert str_model.model_fields["value"].annotation is str

    int_model = get_dynamic_model({"type": "integer"})
    assert issubclass(int_model, BaseModel)
    assert int_model.model_fields["value"].annotation is int

    float_model = get_dynamic_model({"type": "float"})
    assert issubclass(float_model, BaseModel)
    assert float_model.model_fields["value"].annotation is float

    bool_model = get_dynamic_model({"type": "boolean"})
    assert issubclass(bool_model, BaseModel)
    assert bool_model.model_fields["value"].annotation is bool

    # Test object type
    obj_model = get_dynamic_model(
        {
            "type": "object",
            "properties": {"prop1": {"type": "string"}, "prop2": {"type": "integer"}},
        }
    )

    assert issubclass(obj_model, BaseModel)
    assert issubclass(obj_model.model_fields["prop1"].annotation, BaseModel)  # type: ignore
    assert obj_model.model_fields["prop1"].annotation.model_fields["value"].annotation is str
    assert issubclass(obj_model.model_fields["prop2"].annotation, BaseModel)  # type: ignore
    assert obj_model.model_fields["prop2"].annotation.model_fields["value"].annotation is int

    # Test array type
    array_model = get_dynamic_model({"type": "array", "items": {"type": "string"}})
    assert issubclass(array_model, BaseModel)
    items_type = array_model.model_fields["items"].annotation
    assert get_origin(items_type) is list
    item_type = get_args(items_type)[0]
    assert issubclass(item_type, BaseModel)
    assert item_type.model_fields["value"].annotation is str

    # Test nested object type
    nested_obj_model = get_dynamic_model(
        {
            "type": "object",
            "properties": {
                "nested": {
                    "type": "object",
                    "properties": {"prop1": {"type": "string"}, "prop2": {"type": "integer"}},
                }
            },
        }
    )

    assert issubclass(nested_obj_model, BaseModel)
    assert issubclass(nested_obj_model.model_fields["nested"].annotation, BaseModel)  # type: ignore
    nested_model = nested_obj_model.model_fields["nested"].annotation
    assert issubclass(nested_model.model_fields["prop1"].annotation, BaseModel)  # type: ignore
    assert nested_model.model_fields["prop1"].annotation.model_fields["value"].annotation is str
    assert issubclass(nested_model.model_fields["prop2"].annotation, BaseModel)  # type: ignore
    assert nested_model.model_fields["prop2"].annotation.model_fields["value"].annotation is int

    # Test maximum depth exceeded
    with pytest.raises(MaximumDepthExceededError) as excinfo:
        get_dynamic_model(
            {
                "type": "object",
                "properties": {
                    "nested1": {
                        "type": "object",
                        "properties": {
                            "nested2": {
                                "type": "object",
                                "properties": {
                                    "nested3": {
                                        "type": "object",
                                        "properties": {
                                            "nested4": {
                                                "type": "object",
                                                "properties": {"nested5": {"type": "string"}},
                                            }
                                        },
                                    }
                                },
                            }
                        },
                    }
                },
            },
        )
    assert excinfo.value.extra_info["max_depth"] == "5"

    # Test with custom max_depth
    deep_nested_model = get_dynamic_model(
        {
            "type": "object",
            "properties": {
                "nested1": {
                    "type": "object",
                    "properties": {
                        "nested2": {
                            "type": "object",
                            "properties": {"prop": {"type": "string"}},
                        }
                    },
                }
            },
        },
        max_depth=10,
    )
    assert issubclass(deep_nested_model, BaseModel)
    assert issubclass(deep_nested_model.model_fields["nested1"].annotation, BaseModel)  # type: ignore
    nested1_model = deep_nested_model.model_fields["nested1"].annotation
    assert issubclass(nested1_model.model_fields["nested2"].annotation, BaseModel)  # type: ignore
    nested2_model = nested1_model.model_fields["nested2"].annotation
    assert issubclass(nested2_model.model_fields["prop"].annotation, BaseModel)  # type: ignore
    assert nested2_model.model_fields["prop"].annotation.model_fields["value"].annotation is str

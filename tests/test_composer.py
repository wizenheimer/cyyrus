import pytest
from pydantic import BaseModel
from typing import List, Optional

from cyyrus.models.types import merge_pydantic_models  # type: ignore


class ModelA(BaseModel):
    field_a: str
    field_b: int


class ModelB(BaseModel):
    field_c: float
    field_d: bool


def test_merge_pydantic_models():
    MergedModel = merge_pydantic_models([ModelA, ModelB])

    assert issubclass(MergedModel, BaseModel)
    assert set(MergedModel.model_fields.keys()) == {"field_a", "field_b", "field_c", "field_d"}

    instance = MergedModel(field_a="test", field_b=1, field_c=1.5, field_d=True)
    assert instance.field_a == "test"  # type: ignore
    assert instance.field_b == 1  # type: ignore
    assert instance.field_c == 1.5  # type: ignore
    assert instance.field_d is True  # type: ignore


def test_merge_with_python_types():
    MergedModel = merge_pydantic_models([ModelA, str, int])

    assert set(MergedModel.model_fields.keys()) == {"field_a", "field_b", "str", "int"}

    instance = MergedModel(field_a="test", field_b=1, str="python", int=42)
    assert instance.str == "python"
    assert instance.int == 42


def test_merge_with_type_strings():
    MergedModel = merge_pydantic_models([ModelA, "float", "boolean"])

    assert set(MergedModel.model_fields.keys()) == {"field_a", "field_b", "float", "boolean"}

    instance = MergedModel(field_a="test", field_b=1, float=3.14, boolean=False)
    assert instance.float == 3.14
    assert instance.boolean is False


def test_merge_all_types():
    MergedModel = merge_pydantic_models([ModelA, ModelB, str, int, "float", "boolean"])

    expected_fields = {"field_a", "field_b", "field_c", "field_d", "str", "int", "float", "boolean"}
    assert set(MergedModel.model_fields.keys()) == expected_fields


def test_custom_model_name():
    CustomModel = merge_pydantic_models([ModelA], model_name="CustomModel")
    assert CustomModel.__name__ == "CustomModel"


def test_merge_with_optional_fields():
    class ModelWithOptional(BaseModel):
        optional_field: Optional[str] = None

    MergedModel = merge_pydantic_models([ModelA, ModelWithOptional])

    instance = MergedModel(field_a="test", field_b=1)
    assert instance.optional_field is None

    instance = MergedModel(field_a="test", field_b=1, optional_field="present")
    assert instance.optional_field == "present"


def test_merge_with_list_fields():
    class ModelWithList(BaseModel):
        list_field: List[int]

    MergedModel = merge_pydantic_models([ModelA, ModelWithList])

    instance = MergedModel(field_a="test", field_b=1, list_field=[1, 2, 3])
    assert instance.list_field == [1, 2, 3]


def test_error_on_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported model type"):
        merge_pydantic_models([ModelA, 42])  # 42 is neither a type nor a string


def test_error_on_duplicate_field_names():
    class ModelC(BaseModel):
        field_a: float  # This conflicts with ModelA's field_a

    MergedModel = merge_pydantic_models([ModelA, ModelC])

    # The last model's field definition should win
    assert MergedModel.model_fields["field_a"].annotation is float

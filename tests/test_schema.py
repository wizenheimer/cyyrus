import typing
from pydantic import ValidationError
import pytest
from cyyrus.models.column import Column  # type: ignore
from cyyrus.models.dataset import (  # type: ignore
    Dataset,
    DatasetAttributes,
    DatasetMetadata,
    DatasetSampling,
    DatasetShuffle,
    DatasetSplits,
    SpecVersion,
)
from cyyrus.errors.schema import (  # type: ignore
    ColumnIDNotFoundError,
    ColumnTaskIDNotFoundError,
    ColumnTypeNotFoundError,
    DuplicateColumnIDError,
    MaximumDepthExceededError,
)
from cyyrus.models.reference import Reference, ReferenceType  # type: ignore
from cyyrus.models.types import ArrayItems, DataType, ObjectProperty, CustomType, create_dynamic_type  # type: ignore
from cyyrus.models.spec import Spec  # type: ignore
from enum import Enum
from typing import List

from cyyrus.models.task import Task, TaskType  # type: ignore


def test_missing_field():
    invalid_schema = {
        # Missing required fields
        "spec": "v0",
        "dataset": {},
        "tasks": {},
        "types": {},
    }

    with pytest.raises(ValidationError):
        Spec.model_validate(invalid_schema)


def test_column():
    # Test valid Column
    valid_column = Column(column_type="string", task_id="task1")
    assert valid_column.column_type == "string"
    assert valid_column.description == ""
    assert valid_column.task_id == "task1"
    assert valid_column.task_input == {}

    # Test Column with all fields
    full_column = Column(
        column_type="integer",
        description="An integer column",
        task_id="task2",
        task_input={"param1": "value1"},
    )
    assert full_column.column_type == "integer"
    assert full_column.description == "An integer column"
    assert full_column.task_id == "task2"
    assert full_column.task_input == {"param1": "value1"}

    # Test invalid Column (missing required field)
    with pytest.raises(ValidationError):
        Column(description="Invalid column")  # type: ignore


def test_spec_version():
    assert SpecVersion.V0 == "v0"
    assert isinstance(SpecVersion.V0, Enum)


def test_dataset_metadata():
    # Test default values
    default_metadata = DatasetMetadata()
    assert default_metadata.name == "Dataset"
    assert default_metadata.description == "Dataset generated using cyyrus"
    assert default_metadata.tags == ["dataset"]
    assert default_metadata.license == "MIT"
    assert default_metadata.language == "en"

    # Test custom values
    custom_metadata = DatasetMetadata(
        name="Custom Dataset",
        description="A custom dataset",
        tags=["custom", "test"],
        license="Apache-2.0",
        language="fr",
    )
    assert custom_metadata.name == "Custom Dataset"
    assert custom_metadata.description == "A custom dataset"
    assert custom_metadata.tags == ["custom", "test"]
    assert custom_metadata.license == "Apache-2.0"
    assert custom_metadata.language == "fr"


def test_dataset_sampling():
    # Test default value
    default_sampling = DatasetSampling()
    assert default_sampling.percentage == 1

    # Test valid custom value
    valid_sampling = DatasetSampling(percentage=0.5)
    assert valid_sampling.percentage == 0.5

    # Test invalid values
    with pytest.raises(ValidationError):
        DatasetSampling(percentage=0)
    with pytest.raises(ValidationError):
        DatasetSampling(percentage=1.1)


def test_dataset_shuffle():
    # Test default values
    default_shuffle = DatasetShuffle()
    assert default_shuffle.seed == 42
    assert default_shuffle.buffer_size == 1000

    # Test custom values
    custom_shuffle = DatasetShuffle(seed=123, buffer_size=500)
    assert custom_shuffle.seed == 123
    assert custom_shuffle.buffer_size == 500

    # Test invalid buffer_size
    with pytest.raises(ValidationError):
        DatasetShuffle(buffer_size=0)


def test_dataset_splits():
    # Test default values
    default_splits = DatasetSplits()
    assert default_splits.train == 0.8
    assert default_splits.test == 0.1
    assert default_splits.validation == 0.1

    # Test custom values
    custom_splits = DatasetSplits(train=0.7, test=0.2, validation=0.1)
    assert custom_splits.train == 0.7
    assert custom_splits.test == 0.2
    assert custom_splits.validation == 0.1

    # Test invalid values
    with pytest.raises(ValidationError):
        DatasetSplits(train=1.1)  # type: ignore
    with pytest.raises(ValidationError):
        DatasetSplits(train=-0.1)  # type: ignore

    # Test splits normalization
    with pytest.warns():  # type: ignore
        normalized_splits = DatasetSplits(train=0.8, test=0.3, validation=0.3)
        assert (
            normalized_splits.train + normalized_splits.test + normalized_splits.validation  # type: ignore
            == pytest.approx(1.0)
        )


def test_dataset_attributes():
    # Test default values
    default_attrs = DatasetAttributes()
    assert default_attrs.required_columns == []
    assert default_attrs.unique_columns == []
    assert default_attrs.nulls == "include"
    assert default_attrs.references == "include"

    # Test custom values
    custom_attrs = DatasetAttributes(
        required_columns=["col1", "col2"],
        unique_columns=["col3"],
        nulls="exclude",
        references="exclude",
    )
    assert custom_attrs.required_columns == ["col1", "col2"]
    assert custom_attrs.unique_columns == ["col3"]
    assert custom_attrs.nulls == "exclude"
    assert custom_attrs.references == "exclude"

    # Test invalid values
    with pytest.raises(ValidationError):
        DatasetAttributes(nulls="invalid")
    with pytest.raises(ValidationError):
        DatasetAttributes(references="invalid")


def test_dataset():
    # Test default values
    default_dataset = Dataset()
    assert isinstance(default_dataset.metadata, DatasetMetadata)
    assert isinstance(default_dataset.sampling, DatasetSampling)
    assert isinstance(default_dataset.shuffle, DatasetShuffle)
    assert isinstance(default_dataset.splits, DatasetSplits)
    assert isinstance(default_dataset.attributes, DatasetAttributes)

    # Test custom values
    custom_dataset = Dataset(
        metadata=DatasetMetadata(name="Custom Dataset"),
        sampling=DatasetSampling(percentage=0.5),
        shuffle=DatasetShuffle(seed=123),
        splits=DatasetSplits(train=0.7, test=0.3, validation=0),
        attributes=DatasetAttributes(required_columns=["col1"]),
    )
    assert custom_dataset.metadata.name == "Custom Dataset"
    assert custom_dataset.sampling.percentage == 0.5
    assert custom_dataset.shuffle.seed == 123
    assert custom_dataset.splits.train == 0.7
    assert custom_dataset.splits.test == 0.3
    assert custom_dataset.attributes.required_columns == ["col1"]


def test_reference_type():
    assert ReferenceType.DOCUMENT == "document"
    assert isinstance(ReferenceType.DOCUMENT, Enum)


def test_reference():
    # Test valid Reference
    valid_reference = Reference(type=ReferenceType.DOCUMENT, path="/path/to/document")
    assert valid_reference.type == ReferenceType.DOCUMENT
    assert valid_reference.path == "/path/to/document"
    assert valid_reference.description == ""

    # Test Reference with all fields
    full_reference = Reference(
        type=ReferenceType.VISION,
        path=["/path/to/image1", "/path/to/image2"],
        description="Vision reference",
    )
    assert full_reference.type == ReferenceType.VISION
    assert full_reference.path == ["/path/to/image1", "/path/to/image2"]
    assert full_reference.description == "Vision reference"

    # Test invalid Reference (missing required field)
    with pytest.raises(ValidationError):
        Reference(description="Invalid reference")  # type: ignore


def test_spec():
    # Create mock data for testing
    mock_dataset = Dataset()
    mock_reference = {"ref1": Reference(type=ReferenceType.DOCUMENT, path="/path/to/doc")}
    mock_tasks = {"task1": Task(task_type=TaskType.GENERATION, task_properties={})}
    mock_types = {"type1": CustomType(type=DataType.STRING)}
    mock_columns = {"col1": Column(column_type="string", task_id="task1")}

    # Test valid Spec
    valid_spec = Spec(
        spec=SpecVersion.V0,
        dataset=mock_dataset,
        reference=mock_reference,
        tasks=mock_tasks,
        types=mock_types,
        columns=mock_columns,
    )
    assert valid_spec.spec == SpecVersion.V0
    assert isinstance(valid_spec.dataset, Dataset)
    assert "ref1" in valid_spec.reference
    assert "task1" in valid_spec.tasks
    assert "type1" in valid_spec.types
    assert "col1" in valid_spec.columns

    # Test invalid Spec (duplicate column and reference names)
    with pytest.raises(DuplicateColumnIDError):
        Spec(
            spec=SpecVersion.V0,
            dataset=mock_dataset,
            reference={"duplicate": Reference(type=ReferenceType.DOCUMENT, path="/path")},
            tasks=mock_tasks,
            types=mock_types,
            columns={"duplicate": Column(column_type="string", task_id="task1")},
        )

    # Test invalid Spec (missing required column)
    with pytest.raises(ColumnIDNotFoundError):
        Spec(
            spec=SpecVersion.V0,
            dataset=Dataset(attributes=DatasetAttributes(required_columns=["missing_column"])),
            reference=mock_reference,
            tasks=mock_tasks,
            types=mock_types,
            columns=mock_columns,
        )

    # Test invalid Spec (column type not found)
    with pytest.raises(ColumnTypeNotFoundError):
        Spec(
            spec=SpecVersion.V0,
            dataset=mock_dataset,
            reference=mock_reference,
            tasks=mock_tasks,
            types=mock_types,
            columns={"invalid_col": Column(column_type="invalid_type", task_id="task1")},
        )

    # Test invalid Spec (column task ID not found)
    with pytest.raises(ColumnTaskIDNotFoundError):
        Spec(
            spec=SpecVersion.V0,
            dataset=mock_dataset,
            reference=mock_reference,
            tasks=mock_tasks,
            types=mock_types,
            columns={"invalid_col": Column(column_type="string", task_id="invalid_task")},
        )


def test_task_type():
    assert TaskType.GENERATION == "generation"
    assert isinstance(TaskType.GENERATION, Enum)


def test_task():
    # Test valid Task
    valid_task = Task(task_type=TaskType.GENERATION, task_properties={})
    assert valid_task.task_type == TaskType.GENERATION
    assert valid_task.task_properties == {}

    # Test Task with properties
    task_with_props = Task(
        task_type=TaskType.CATEGORIZATION,
        task_properties={"num_categories": 5, "model": "gpt-3.5-turbo"},
    )
    assert task_with_props.task_type == TaskType.CATEGORIZATION
    assert task_with_props.task_properties == {"num_categories": 5, "model": "gpt-3.5-turbo"}

    # Test invalid Task (missing required field)
    with pytest.raises(ValidationError):
        Task(task_properties={})  # type: ignore


def test_data_type():
    assert DataType.STRING == "string"
    assert isinstance(DataType.STRING, Enum)


def test_object_property():
    # Test with DataType
    prop1 = ObjectProperty(type=DataType.STRING)
    assert prop1.type == DataType.STRING

    # Test with invalid type
    with pytest.raises(ValidationError):
        ObjectProperty(type=123)  # type: ignore


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
    assert valid_type.dynamic_model is not None

    # Test Type with properties
    type_with_props = CustomType(
        type=DataType.OBJECT, properties={"prop1": ObjectProperty(type=DataType.INTEGER)}
    )
    assert type_with_props.type == DataType.OBJECT
    assert "prop1" in type_with_props.properties  # type: ignore
    assert type_with_props.properties["prop1"].type == DataType.INTEGER  # type: ignore
    assert type_with_props.dynamic_model is not None

    # Test Type with items
    type_with_items = CustomType(type=DataType.ARRAY, items=ArrayItems(type=DataType.STRING))
    assert type_with_items.type == DataType.ARRAY
    assert type_with_items.items.type == DataType.STRING  # type: ignore
    assert type_with_items.dynamic_model is not None

    # Test invalid Type (missing required field)
    with pytest.raises(ValidationError):
        CustomType()

    # Test Type with invalid dynamic model
    with pytest.raises(ValidationError):
        CustomType(
            type="invalid_type"
        )  # Deviates from the schema, which doesn't allow custom/aliased types


def test_create_dynamic_type():
    # Test simple types
    str_type = create_dynamic_type({"type": "string"})
    assert str_type is str

    int_type = create_dynamic_type({"type": "integer"})
    assert int_type is int

    float_type = create_dynamic_type({"type": "float"})
    assert float_type is float

    bool_type = create_dynamic_type({"type": "boolean"})
    assert bool_type is bool

    # Test object type
    obj_type = create_dynamic_type(
        {
            "type": "object",
            "properties": {"prop1": {"type": "string"}, "prop2": {"type": "integer"}},
        }
    )

    assert typing.get_type_hints(obj_type) == {
        "prop1": str,
        "prop2": int,
    }

    # Test array type
    array_type = create_dynamic_type({"type": "array", "items": {"type": "string"}})
    assert array_type == List[str]

    # Test nested object type
    nested_obj_type = create_dynamic_type(
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

    assert nested_obj_type.model_json_schema() == {
        "$defs": {
            "DynamicModel": {
                "properties": {
                    "prop1": {"title": "Prop1", "type": "string"},
                    "prop2": {"title": "Prop2", "type": "integer"},
                },
                "required": ["prop1", "prop2"],
                "title": "DynamicModel",
                "type": "object",
            },
        },
        "properties": {"nested": {"$ref": "#/$defs/DynamicModel"}},
        "required": ["nested"],
        "title": "DynamicModel",
        "type": "object",
    }

    # Test maximum depth exceeded
    with pytest.raises(MaximumDepthExceededError):
        create_dynamic_type(
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

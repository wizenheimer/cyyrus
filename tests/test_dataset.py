import pytest
from cyyrus.models.dataset import (  # type: ignore
    Dataset,
    DatasetAttributes,
    DatasetMetadata,
    DatasetShuffle,
    DatasetSplits,
)
from pydantic import ValidationError


def test_dataset_metadata():
    # Test default values
    default_metadata = DatasetMetadata()
    assert default_metadata.name == "Dataset"
    assert default_metadata.description == "Dataset generated using cyyrus"
    assert default_metadata.tags == ["dataset"]
    assert default_metadata.license == "MIT"

    # Test custom values
    custom_metadata = DatasetMetadata(
        name="Custom Dataset",
        description="A custom dataset",
        tags=["custom", "test"],
        license="Apache-2.0",
    )
    assert custom_metadata.name == "Custom Dataset"
    assert custom_metadata.description == "A custom dataset"
    assert custom_metadata.tags == ["custom", "test"]
    assert custom_metadata.license == "Apache-2.0"


def test_dataset_shuffle():
    # Test default values
    default_shuffle = DatasetShuffle()
    assert default_shuffle.seed == 42

    # Test custom values
    custom_shuffle = DatasetShuffle(seed=123, buffer_size=500)
    assert custom_shuffle.seed == 123

    # Test invalid seed
    with pytest.raises(ValidationError):
        DatasetShuffle(seed="awesome")  # type: ignore


def test_dataset_splits():
    # Test default values
    with pytest.warns():
        default_splits = DatasetSplits()
    assert default_splits.train == 0.8
    assert default_splits.test == 0.2

    # Test custom values
    custom_splits = DatasetSplits(train=0.5, test=0.5)
    assert custom_splits.train == 0.5
    assert custom_splits.test == 0.5

    # Test invalid values
    with pytest.raises(ValidationError):
        DatasetSplits(train=1.1)  # type: ignore
    with pytest.raises(ValidationError):
        DatasetSplits(train=-0.1)  # type: ignore

        # Test splits normalization
    normalized_splits = DatasetSplits(train=0.8, test=0.1)
    assert normalized_splits.train + normalized_splits.test == pytest.approx(1.0)  # type: ignore


def test_dataset_attributes():
    # Test default values
    default_attrs = DatasetAttributes()
    assert default_attrs.required_columns == []
    assert default_attrs.unique_columns == []
    assert default_attrs.nulls == "include"

    # Test custom values
    custom_attrs = DatasetAttributes(
        required_columns=["col1", "col2"],
        unique_columns=["col3"],
        nulls="exclude",
    )
    assert custom_attrs.required_columns == ["col1", "col2"]
    assert custom_attrs.unique_columns == ["col3"]
    assert custom_attrs.nulls == "exclude"

    # Test invalid values
    with pytest.raises(ValidationError):
        DatasetAttributes(nulls="invalid")


def test_dataset():
    # Test default values
    with pytest.warns():
        default_dataset = Dataset()
    assert isinstance(default_dataset.metadata, DatasetMetadata)
    assert isinstance(default_dataset.shuffle, DatasetShuffle)
    assert isinstance(default_dataset.splits, DatasetSplits)
    assert isinstance(default_dataset.attributes, DatasetAttributes)

    # Test custom values
    custom_dataset = Dataset(
        metadata=DatasetMetadata(name="Custom Dataset"),
        shuffle=DatasetShuffle(seed=123),
        splits=DatasetSplits(train=0.7, test=0.3, seed=42),
        attributes=DatasetAttributes(required_columns=["col1"]),
    )
    assert custom_dataset.metadata.name == "Custom Dataset"
    assert custom_dataset.shuffle.seed == 123
    assert custom_dataset.splits.train == 0.7
    assert custom_dataset.splits.test == 0.3
    assert custom_dataset.attributes.required_columns == ["col1"]

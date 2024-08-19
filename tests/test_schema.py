from enum import Enum

import pytest
from cyyrus.errors.column import (  # type: ignore
    ColumnIDNotFoundError,
    ColumnTaskIDNotFoundError,
    ColumnTypeNotFoundError,
)
from cyyrus.models.column import Column  # type: ignore
from cyyrus.models.dataset import (  # type: ignore
    Dataset,
    DatasetAttributes,
    SpecVersion,
)
from cyyrus.models.spec import Spec  # type: ignore
from cyyrus.models.task import Task  # type: ignore
from cyyrus.models.task_type import TaskType  # type: ignore
from cyyrus.models.types import (  # type: ignore
    CustomType,
    DataType,
)
from pydantic import ValidationError


def test_missing_field():
    invalid_schema = {
        # Missing required fields
        "spec": "v0",
        "tasks": {},
        "types": {},
    }

    with pytest.raises(ValidationError):
        Spec.model_validate(invalid_schema)


def test_spec_version():
    assert SpecVersion.V0 == "v0"
    assert isinstance(SpecVersion.V0, Enum)


def test_spec():
    # Create mock data for testing
    with pytest.warns():
        mock_dataset = Dataset()
    mock_tasks = {"task1": Task(task_type=TaskType.DEFAULT, task_properties={})}
    mock_types = {"type1": CustomType(type=DataType.STRING)}
    mock_columns = {"col1": Column(column_type="string", task_id="task1")}

    # Test valid Spec
    valid_spec = Spec(
        spec=SpecVersion.V0,
        dataset=mock_dataset,
        tasks=mock_tasks,
        types=mock_types,
        columns=mock_columns,
    )
    assert valid_spec.spec == SpecVersion.V0
    assert isinstance(valid_spec.dataset, Dataset)
    assert "task1" in valid_spec.tasks
    assert "type1" in valid_spec.types
    assert "col1" in valid_spec.columns

    # Test invalid Spec (missing required column)
    with pytest.raises(ColumnIDNotFoundError):
        with pytest.warns():
            dataset = Dataset(attributes=DatasetAttributes(required_columns=["missing_column"]))
        Spec(
            spec=SpecVersion.V0,
            dataset=dataset,
            tasks=mock_tasks,
            types=mock_types,
            columns=mock_columns,
        )

    # Test invalid Spec (column type not found)
    with pytest.raises(ColumnTypeNotFoundError):
        Spec(
            spec=SpecVersion.V0,
            dataset=mock_dataset,
            tasks=mock_tasks,
            types=mock_types,
            columns={"invalid_col": Column(column_type="invalid_type", task_id="task1")},
        )

    # Test invalid Spec (column task ID not found)
    with pytest.raises(ColumnTaskIDNotFoundError):
        Spec(
            spec=SpecVersion.V0,
            dataset=mock_dataset,
            tasks=mock_tasks,
            types=mock_types,
            columns={"invalid_col": Column(column_type="string", task_id="invalid_task")},
        )

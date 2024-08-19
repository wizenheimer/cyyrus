import pytest
from cyyrus.models.column import Column  # type: ignore
from pydantic import ValidationError


def test_column():
    # Test valid Column
    valid_column = Column(column_type="string", task_id="task1")
    assert valid_column.column_type == "string"
    assert valid_column.description == ""
    assert valid_column.task_id == "task1"
    assert valid_column.task_input == []

    # Test Column with all fields
    full_column = Column(
        column_type="integer",
        description="An integer column",
        task_id="task2",
        task_input=[
            "param1",
            "value1",
        ],
    )
    assert full_column.column_type == "integer"
    assert full_column.description == "An integer column"
    assert full_column.task_id == "task2"
    assert full_column.task_input == [
        "param1",
        "value1",
    ]

    # Test invalid Column (missing required field)
    with pytest.raises(ValidationError):
        Column(description="Invalid column")  # type: ignore

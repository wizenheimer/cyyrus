from enum import Enum

import pytest
from cyyrus.models.task import Task  # type: ignore
from cyyrus.models.task_model import LargeLanguageModels  # type: ignore
from cyyrus.models.task_type import TASK_PROPERTIES, TaskType  # type: ignore
from cyyrus.models.types import (  # type: ignore
    DataType,
    ObjectProperty,
)
from pydantic import ValidationError


def create_task(task_type, properties):
    return Task(task_type=task_type, task_properties=properties)


def test_valid_task_creation():
    for task_type in TaskType:
        properties = {}
        for prop, (_, default) in TASK_PROPERTIES[task_type]["required"].items():
            if default is ...:
                properties[prop] = "test_value"
        task = create_task(task_type, properties)
        assert task.task_type == task_type
        assert all(prop in task.task_properties for prop in TASK_PROPERTIES[task_type]["required"])


def test_missing_required_property():
    with pytest.raises(ValidationError):
        create_task(TaskType.PARSING, {})


def test_invalid_property_type():
    with pytest.raises(ValidationError):
        create_task(TaskType.PARSING, {"directory": 123, "file_type": "txt"})


def test_all_task_types():
    for task_type in TaskType:
        properties = {}
        for prop, (_, default) in TASK_PROPERTIES[task_type]["required"].items():
            if default is ...:
                properties[prop] = "test_value"
        task = create_task(task_type, properties)
        assert task.task_type == task_type


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


def test_default_values():
    task = create_task(TaskType.PARSING, {"directory": "test", "file_type": "txt"})
    assert task.task_properties["max_depth"] == 5


def test_optional_property_override():
    task = create_task(TaskType.PARSING, {"directory": "test", "file_type": "txt", "max_depth": 10})
    assert task.task_properties["max_depth"] == 10


def test_extra_properties_ignored():
    task = create_task(
        TaskType.PARSING, {"directory": "test", "file_type": "txt", "extra_prop": "ignored"}
    )
    assert "extra_prop" not in task.task_properties


def test_enum_property():
    task = create_task(
        TaskType.GENERATION, {"prompt": "test", "model": LargeLanguageModels.GPT_4O_MINI}
    )
    assert isinstance(task.task_properties["model"], LargeLanguageModels)
    assert task.task_properties["model"] == LargeLanguageModels.GPT_4O_MINI


def test_enum_property_string_input():
    task = create_task(TaskType.GENERATION, {"prompt": "test", "model": "gpt-4o-mini"})
    assert isinstance(task.task_properties["model"], LargeLanguageModels)
    assert task.task_properties["model"] == LargeLanguageModels.GPT_4O_MINI


def test_missing_optional_property():
    task = create_task(TaskType.AUDIOEXTRACTION, {})
    assert "max_duration" in task.task_properties
    assert task.task_properties["max_duration"] == 60

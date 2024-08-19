from enum import Enum
from typing import Any, Dict, List, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.functional_validators import model_validator

from cyyrus.models.task_type import TASK_PROPERTIES, TaskType


class Task(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_type: TaskType
    task_properties: Dict[str, Any]

    @model_validator(mode="after")
    def validate_task_properties(self):
        task_type = self.task_type
        properties = TASK_PROPERTIES.get(task_type, {})
        required_props = properties.get("required", {})
        optional_props = properties.get("optional", {})

        validated_props = {}

        def validate_and_convert(value, expected_type):
            if get_origin(expected_type) is Union:
                for t in get_args(expected_type):
                    try:
                        return validate_and_convert(value, t)
                    except (ValueError, TypeError):
                        continue
                raise ValueError(f"Value {value} does not match any type in {expected_type}")
            elif get_origin(expected_type) is List:
                if not isinstance(value, list):
                    raise TypeError(f"Expected a list, got {type(value)}")
                return [validate_and_convert(item, get_args(expected_type)[0]) for item in value]
            elif isinstance(expected_type, type) and issubclass(expected_type, Enum):
                if isinstance(value, expected_type):
                    return value
                try:
                    return expected_type(value)
                except ValueError:
                    raise ValueError(f"Invalid enum value: {value} for {expected_type}")
            elif not isinstance(value, expected_type):
                raise TypeError(f"Expected {expected_type}, got {type(value)}")
            return value

        for prop, (prop_type, default_value) in {**required_props, **optional_props}.items():
            if prop in self.task_properties:
                try:
                    validated_props[prop] = validate_and_convert(
                        self.task_properties[prop], prop_type
                    )
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid value for {prop}: {str(e)}")
            elif prop in required_props:
                if default_value is ...:
                    raise ValueError(f"Missing required property for {task_type}: {prop}")
                validated_props[prop] = default_value
            elif prop in optional_props and default_value is not ...:
                validated_props[prop] = default_value

        self.task_properties = validated_props
        return self

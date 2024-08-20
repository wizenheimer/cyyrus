from typing import Any, Dict

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.functional_validators import model_validator

from cyyrus.models.task_type import TASK_PROPERTIES, TaskType


class Task(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    task_type: TaskType
    task_properties: Dict[str, Any]

    @model_validator(mode="after")
    def validate_task_properties(self):
        required_props, optional_props = TaskPropertyUtils.get_task_property(
            self.task_type,
        )

        validated_props = {}

        for prop, (prop_type, default_value) in {**required_props, **optional_props}.items():
            if prop in self.task_properties:
                try:
                    validated_props[prop] = prop_type(
                        self.task_properties[prop],
                    )
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid value for {prop}: {str(e)}")
            elif prop in required_props:
                if default_value is ...:
                    raise ValueError(f"Missing required property {prop} for {self.task_type}")
                validated_props[prop] = default_value
            elif prop in optional_props and default_value is not ...:
                validated_props[prop] = default_value

        self.task_properties = validated_props
        return self


class TaskPropertyUtils:
    @staticmethod
    def get_task_property(
        task_type: TaskType,
    ) -> Any:
        properties = TASK_PROPERTIES.get(
            task_type,
            {},
        )
        required_props = properties.get(
            "required",
            {},
        )
        optional_props = properties.get(
            "optional",
            {},
        )

        return required_props, optional_props

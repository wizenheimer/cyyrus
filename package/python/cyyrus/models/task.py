from typing import Any, Dict

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.functional_validators import model_validator

from cyyrus.models.task_type import TASK_PROPERTIES, TaskType
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


class Task(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    task_type: TaskType
    task_properties: Dict[str, Any]

    @model_validator(mode="after")
    def validate_task_properties(self):
        """
        Validate the task properties
        """
        logger.debug(f"Validating task properties for {self.task_type}")
        required_props, optional_props = TaskPropertyUtils.get_task_property(
            self.task_type,
        )

        all_props = {
            **required_props,
            **optional_props,
        }

        for prop, (prop_type, default_value) in all_props.items():
            if prop in self.task_properties:
                try:
                    self.task_properties[prop] = prop_type(
                        self.task_properties[prop],
                    )
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid value for {prop}: {str(e)}")
            elif prop in required_props and default_value is ...:
                raise ValueError(f"Missing required property {prop} for {self.task_type}")
            elif default_value is not ...:
                self.task_properties[prop] = default_value

        logger.debug(f"Task properties {list(self.task_properties.keys())[:2]}... validated")
        return self


class TaskPropertyUtils:
    @staticmethod
    def get_task_property(
        task_type: TaskType,
    ) -> Any:
        """
        Get the required and optional properties for a given task type
        """
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

        logger.debug(f"Fetched Task properties for {task_type}")
        return required_props, optional_props

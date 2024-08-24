import base64
import copy
import inspect
import io
import json
import string
import sys
from functools import lru_cache
from typing import Any, Dict, List

import litellm
from litellm import supports_vision  # type: ignore

from cyyrus.models.options import LargeLanguageModels
from cyyrus.models.task_type import TaskType
from cyyrus.tasks.base import BaseTask
from cyyrus.utils.errors import error_handler
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)

catch_all = error_handler(
    exceptions=Exception,  # This will catch all exceptions
    handler=None,
    logger=logger,
    retries=1,
    default_return=None,
)


class SuppressOutput:
    def __init__(
        self,
    ):
        self._stdout = None
        self._stderr = None

    def __enter__(
        self,
    ):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):
        sys.stdout = self._stdout
        sys.stderr = self._stderr


class GenerationTask(BaseTask):
    TASK_ID = TaskType.GENERATION

    SUPPORTS_REFERENCE_FREE_EXECUTION = True
    DEFAULT_MODEL = LargeLanguageModels.GPT_4O_MINI
    DEFAULT_PROMPT = "Convert the corpus into a usable dataset"
    MAX_EPOCH = 100

    def __init__(
        self,
        column_name: str,
        task_properties: Dict[str, Any],
    ) -> None:
        super().__init__(column_name, task_properties)

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Perform the generation task.
        """
        logger.debug(f"Executing generation task with {self.TASK_ID} ...")

        return ModelUtils.generation(
            task_input=task_input,
            task_property=self.task_properties,
        )

    def _generate_references(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Attempt to generate the reference data for the task, using the task properties
        """
        max_epochs = self._get_task_property(
            key="max_epochs",
            default=GenerationTask.MAX_EPOCH,
        )
        # Attempt to generate the reference data
        logger.debug(f"Generating references for task {self.TASK_ID} with {max_epochs} epochs ...")
        return [{} for _ in range(max_epochs)]


class ModelUtils:

    @staticmethod
    @lru_cache(maxsize=1)
    def get_valid_completion_args():
        # Inspect the litellm.completion function
        completion_params = inspect.signature(litellm.completion).parameters
        # Return a set of valid argument names
        return set(completion_params.keys())

    @staticmethod
    def safe_format(
        template: str | List[str],
        **kwargs: Any,
    ) -> str:
        logger = logger = get_logger(__name__)
        logger.debug("Attempting to format response with template")

        if isinstance(template, list):
            # If template is a list, join it into a single string
            template = " ".join(template)

        # Use a custom formatter to handle missing keys
        class DefaultFormatter(string.Formatter):
            def __init__(self, default=""):
                self.default = default

            def get_value(self, key, args, kwargs):
                if isinstance(key, str):
                    return kwargs.get(key, self.default)
                else:
                    return string.Formatter.get_value(key, args, kwargs)  # type: ignore

        return DefaultFormatter().format(template, **kwargs)

    @staticmethod
    def log_completion_args(
        completion_args: Dict[str, Any],
    ):
        logger.debug("logging completion arguments ...")
        redacted_log_arguments = [
            "api_key",
        ]
        for key, value in completion_args.items():
            logger.debug(
                f"{key}: {value}" if key not in redacted_log_arguments else f"{key}: <redacted>"
            )

    @staticmethod
    @catch_all
    def generation(
        task_property: Dict[str, Any],
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Process the model.
        """
        logger.debug("Processing generation task ...")

        # Create a copy of the task property to avoid modifying the original
        generation_property = copy.deepcopy(task_property)

        # Converts the prompt into a formatted string of messages
        prompt = generation_property.pop("prompt", "")
        formatted_prompt = ModelUtils.safe_format(
            prompt,
            **task_input,
        )
        content = [
            {
                "type": "text",
                "text": formatted_prompt,
            }
        ]

        model = generation_property.get(
            "model",
            LargeLanguageModels.GPT_4O_MINI,
        )

        img_key = ModelUtils.find_multimodal_key(task_input)
        if img_key and supports_vision(model=model):
            base64_image = task_input.get(img_key)
            image_arg = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "low",
                },
            }
            content.append(image_arg)

        # Create the messages list with the proper structure
        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]
        # Update generation_property with the correct messages format
        generation_property["messages"] = messages

        if generation_property.get("response_format", None) is None:
            logger.debug("No response format specified, defaulting to unstructured text ...")
            generation_property.pop("response_format", None)
        else:
            logger.debug("Response format specified, attempting to process ...")

        valid_args = ModelUtils.get_valid_completion_args()

        filtered_generation_property = {
            k: v for k, v in generation_property.items() if k in valid_args
        }
        ModelUtils.log_completion_args(filtered_generation_property)

        # add conditional log suppression
        with SuppressOutput():
            response = litellm.completion(
                **filtered_generation_property,
            )

        result = response.choices[0].message.content  # type: ignore

        if "response_format" in generation_property.keys():
            result = ModelUtils.safe_str_to_dict(result)

        return result

    @staticmethod
    def safe_str_to_dict(
        input_data: Any,
    ):
        """
        Safely convert a string to a dictionary if possible.
        If input is already a dictionary, return it as is.
        If conversion fails, return the original string.

        Args:
        input_data (Union[str, dict]): The input data to convert.

        Returns:
        Union[str, dict]: The converted dictionary or the original string.
        """
        logger.debug("Attempting to convert string to dictionary ...")
        if isinstance(input_data, dict):
            return input_data

        if isinstance(input_data, str):
            try:
                return json.loads(input_data)
            except json.JSONDecodeError:
                return input_data

        return input_data  # Return as is for any other type

    @staticmethod
    def find_multimodal_key(
        task_input: Dict[str, Any],
    ):
        logger.debug("Attempting to find multimodal key in task input ...")
        for key, value in task_input.items():
            if isinstance(value, str) and ModelUtils.is_base64_image(value):
                return key
        return None

    @staticmethod
    def is_base64_image(value: str) -> bool:
        """
        Check if a string is a base64 encoded image.
        """
        logger.debug("Checking if string is a base64 encoded image ...")
        try:
            # Attempt to decode the string
            decoded = base64.b64decode(
                value,
            )
            # Check for common image headers (you might want to expand this list)
            return decoded.startswith(
                (
                    b"\xFF\xD8\xFF",
                    b"\x89PNG\r\n\x1a\n",
                    b"GIF87a",
                    b"GIF89a",
                )
            )
        except Exception as _:
            return False

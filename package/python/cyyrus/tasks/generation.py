import copy
import inspect
from functools import lru_cache
from typing import Any, Dict, List, Set

from openai import OpenAI

from cyyrus.models.options import LargeLanguageModels, VisionLanguageModels
from cyyrus.models.task_type import TaskType
from cyyrus.models.types import DefaultModel
from cyyrus.tasks.base import BaseTask
from cyyrus.tasks.utils import Base64ImageFinder, GeneralUtils, NestedDictAccessor
from cyyrus.utils.errors import error_handler
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)

catch_all_return_none = error_handler(
    exceptions=Exception,  # This will catch all exceptions
    handler=None,
    logger=logger,
    retries=1,
    default_return=None,
)


class GenerationTask(BaseTask):
    TASK_ID = TaskType.GENERATION

    SUPPORTS_REFERENCE_FREE_EXECUTION = True
    DEFAULT_MODEL = LargeLanguageModels.GPT_4O_MINI
    DEFAULT_PROMPT = "Convert the corpus into a usable dataset"
    MAX_EPOCH = 100

    @lru_cache
    def get_valid_completion_args(self) -> Set[str]:
        completion_params = inspect.signature(self.client.chat.completions.create).parameters
        # Return a set of valid argument names
        return set(completion_params.keys())

    def __init__(
        self,
        column_name: str,
        task_properties: Dict[str, Any],
    ) -> None:
        super().__init__(
            column_name,
            task_properties,
        )
        api_key = NestedDictAccessor.get_nested_value(
            task_properties,
            "api_key",
        )
        self.client = OpenAI(
            api_key=api_key,
        )

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Perform the generation task.
        """
        logger.debug(f"Executing generation task with {self.TASK_ID} ...")
        return self.inference(task_input=task_input)

    @catch_all_return_none
    def inference(self, task_input: Dict[str, Any]) -> Any:
        # Get Prompt from Task Property
        prompt = NestedDictAccessor.get_nested_value(
            self.task_properties,
            key="prompt",
            default=GenerationTask.DEFAULT_PROMPT,
        )

        # Process Prompt
        formatted_prompt = GeneralUtils.populate_template(
            prompt,
            self.task_properties | task_input,  # Merge task_properties and task_input
        )
        logger.debug(f"Formatted Prompt: {formatted_prompt}")

        # Pop prompt parameter
        generation_properties = copy.deepcopy(self.task_properties)
        generation_properties.pop("prompt", None)

        # Format OpenAI Call
        content = [
            {
                "type": "text",
                "text": formatted_prompt,
            }
        ]

        # Generation Model
        model = generation_properties.get(
            "model",
            LargeLanguageModels.GPT_4O_MINI,
        )

        # Incase model supports vision params
        if GenerationTask.supports_vision(model=model):
            # Find base64 encoded images in the task_input
            img_keys = Base64ImageFinder.find_base64_encoded_keys(task_input=task_input)
            logger.debug(f"Found {len(img_keys)} base64 images in task input ...")

            for img_key in img_keys:
                base64_image = NestedDictAccessor.get_nested_value(
                    task_input,
                    img_key,
                    None,
                )
                if base64_image:
                    image_arg = {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",  # TODO(wizenheimer): add support for other image types
                            "detail": "low",  # TODO(wizenheimer): make this configurable
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
        generation_properties["messages"] = messages

        # Check if structured prompting is supported
        if generation_properties.get("response_format", None) is None:
            logger.debug("No response format specified, defaulting to unstructured text ...")
            generation_properties["response_format"] = DefaultModel
        else:
            logger.debug("Response format specified, attempting to process ...")

        # Filter out unnecessary properties form generation properties
        filtered_generation_property = {
            k: v for k, v in generation_properties.items() if k in self.get_valid_completion_args()
        }

        # Perform completion and handle errors
        response = self.client.beta.chat.completions.parse(**filtered_generation_property)

        # Return results
        if response.choices[0].message.refusal:
            logger.error(f"Request refused: {response.choices[0].message.refusal}")
            return None

        if generation_properties.get("response_format", None) == DefaultModel:
            return response.choices[0].message.parsed.model_dump().get("value", None)  # type: ignore

        return response.choices[0].message.parsed.model_dump()  # type: ignore

    def _generate_references(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Attempt to generate the reference data for the task, using the task properties
        """
        max_epochs = NestedDictAccessor.get_nested_value(
            self.task_properties,
            "max_epochs",
            GenerationTask.MAX_EPOCH,
        )

        # Attempt to generate the reference data
        logger.debug(f"Generating references for task {self.TASK_ID} with {max_epochs} epochs ...")
        return [{} for _ in range(max_epochs)]

    @staticmethod
    def supports_vision(
        model: str,
    ) -> bool:
        """
        Check if the model supports vision parameters.
        """
        return model in VisionLanguageModels.__members__.values()

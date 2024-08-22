import base64
from typing import Any, Dict, List

from pydantic.main import BaseModel

from cyyrus.models.options import LargeLanguageModels
from cyyrus.models.task_type import TaskType
from cyyrus.models.types import DefaultModel
from cyyrus.tasks.base import BaseTask


class GenerationTask(BaseTask):
    TASK_ID = TaskType.GENERATION

    SUPPORTS_REFERENCE_FREE_EXECUTION = True
    DEFAULT_MODEL = LargeLanguageModels.GPT_4O_MINI
    DEFAULT_PROMPT = "Convert the corpus into a usable dataset"
    MAX_EPOCH = 100

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Perform the generation task.
        """
        prompt = self._get_task_property(
            key="prompt",
            default=GenerationTask.DEFAULT_PROMPT,
        )
        model = self._get_task_property(
            key="model",
            default=GenerationTask.DEFAULT_MODEL,
        )

        return ModelUtils.generation(
            model=model,
            prompt=prompt,
            task_input=task_input,
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
        return [{} for _ in range(max_epochs)]


class ModelUtils:
    @staticmethod
    def generation(
        model: LargeLanguageModels,
        prompt: str,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Process the model.
        """
        is_multimodal = any(
            isinstance(value, str) and ModelUtils.is_base64_image(value)
            for value in task_input.values()
        )

        response_format = task_input.get(
            "response_format",
            DefaultModel,
        )

        if is_multimodal:
            # Trigger multi-modal generation using GPT-4 Vision
            return ModelUtils.multimodal_generation(
                model=model,
                prompt=prompt,
                response_format=response_format,
            )
        else:
            # Trigger text-based generation using GPT-4
            formatted_prompt = prompt.format(
                **task_input,
            )

        return {
            "prompt": formatted_prompt,
            "model": model,
        }

    @staticmethod
    def is_base64_image(value: str) -> bool:
        """
        Check if a string is a base64 encoded image.
        """
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

    @staticmethod
    def multimodal_generation(
        model: LargeLanguageModels,
        prompt: str,
        response_format: type[BaseModel],
    ) -> Any:
        """
        Handle multi-modal generation using GPT-4 Vision.
        """
        # TODO: Placeholder for multi-modal generation logic
        # TODO: Trigger generation with response format
        # TODO: Export the generated data into a dictionary
        return {
            "type": "multi-modal",
            "prompt": prompt,
            "model": model,
            "response_format": response_format.model_fields,
        }

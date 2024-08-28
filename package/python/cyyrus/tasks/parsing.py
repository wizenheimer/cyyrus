import base64
import copy
import inspect
import os
import warnings
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from openai import OpenAI
from pdf2image import convert_from_path
from PIL import Image
from pydub import AudioSegment

from cyyrus.models.options import ParsedFormat
from cyyrus.models.task_type import TaskType
from cyyrus.models.types import MarkdownModel
from cyyrus.tasks.base import BaseTask
from cyyrus.tasks.utils import Base64ImageFinder, GeneralUtils, NestedDictAccessor
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


# For reference based generation, there's always a one-to-one mapping between the input and output
# For instance, for a given PDF file, we can generate multiple images, so the resulting output would be a list of images encoded in base64
# For reference free generation, there's no such mapping constraint
# Hence, the output would be a single image encoded in base64
class ParsingTask(BaseTask):
    # The task ID is used to identify the task type
    TASK_ID = TaskType.PARSING

    # This flag indicates whether the task supports reference-free execution
    SUPPORTS_REFERENCE_FREE_EXECUTION = True

    # Default values for task properties
    DEFAULT_DIRECTORY = str(Path.cwd())
    DEFAULT_FILE_TYPE = "pdf"
    DEFAULT_MAX_DEPTH = 5
    DEFAULT_PARSED_FORMAT = ParsedFormat.BASE64

    EXPECTED_KEY = "path"

    DEFAULT_PROMPT = """Convert the following image to markdown.
    Return only the markdown with no explanation text.
    Do not exclude any content from the image."""

    # At present, we support parsing of PDF and image files
    DOCUMENT_TYPE = [
        "pdf",
    ]
    IMAGE_TYPE = [
        "png",
        "jpg",
        "jpeg",
    ]

    def __init__(
        self,
        column_name: str,
        task_properties: Dict[str, Any],
    ) -> None:
        """
        Initialize the parsing task.
        """
        super().__init__(
            column_name,
            task_properties,
        )
        # Set the default prompt in case it is not provided
        self.task_properties["prompt"] = (
            ParsingTask.DEFAULT_PROMPT
            if "prompt" not in self.task_properties
            else self.task_properties["prompt"]
        )

        parsed_format = NestedDictAccessor.get_nested_value(
            data=self.task_properties,
            key="parsed_format",
            default=ParsingTask.DEFAULT_PARSED_FORMAT,
        )

        if parsed_format == ParsedFormat.MARKDOWN:
            api_key = NestedDictAccessor.get_nested_value(
                data=self.task_properties,
                key="api_key",
                default=None,
            )
            self.client = OpenAI(api_key=api_key)

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Perform the parsing task.
        """
        pass
        path = NestedDictAccessor.get_nested_value(
            data=task_input,
            key=ParsingTask.EXPECTED_KEY,
            default=ParsingTask.DEFAULT_DIRECTORY,
        )
        file_type = NestedDictAccessor.get_nested_value(
            data=self.task_properties,
            key="file_type",
            default=ParsingTask.DEFAULT_FILE_TYPE,
        )
        parsed_format = NestedDictAccessor.get_nested_value(
            data=self.task_properties,
            key="parsed_format",
            default=ParsingTask.DEFAULT_PARSED_FORMAT,
        )

        # Process the file based on its type,
        # Incase the output is required in markdown or base64 format, we need to convert the output to base64
        if file_type in ParsingTask.DOCUMENT_TYPE:
            intermediate_results = DocUtils._process_document(
                path,
                return_base64=parsed_format == ParsedFormat.BASE64
                or parsed_format == ParsedFormat.MARKDOWN,
            )
        elif file_type in ParsingTask.IMAGE_TYPE:
            intermediate_results = ImageUtils._process_image(
                path,
                return_base64=parsed_format == ParsedFormat.BASE64
                or parsed_format == ParsedFormat.MARKDOWN,
            )

        final_result = []
        # Convert the intermediate results to the required format
        if parsed_format == ParsedFormat.MARKDOWN:
            # Generate the final result
            for intermediate_result in intermediate_results:
                # Convert the image to markdown
                base64_image = (
                    ImageUtils._image_to_base64(intermediate_result)
                    if isinstance(intermediate_result, Image.Image)
                    else intermediate_result
                )
                # Generate the final result
                final_result.append(
                    self._trigger_generation(
                        task_input={
                            "image": base64_image,
                        }
                    )
                )
        else:
            final_result = intermediate_results

        # Return the final result
        return final_result

    @lru_cache
    def get_valid_completion_args(self) -> Set[str]:
        completion_params = inspect.signature(self.client.chat.completions.create).parameters
        # Return a set of valid argument names
        return set(completion_params.keys())

    def _trigger_generation(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Trigger the generation task.
        """
        # Get Prompt from Task Property
        generation_properties = copy.deepcopy(self.task_properties)
        generation_properties.pop("prompt", None)

        prompt = NestedDictAccessor.get_nested_value(
            self.task_properties,
            key="prompt",
            default=ParsingTask.DEFAULT_PROMPT,
        )

        # Format the Prompt
        formatted_prompt = GeneralUtils.populate_template(
            prompt,
            self.task_properties | task_input,  # Merge task_properties and task_input
        )

        # Format OpenAI Call
        content = [
            {
                "type": "text",
                "text": formatted_prompt,
            }
        ]

        img_keys = Base64ImageFinder.find_base64_encoded_keys(task_input=task_input)

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

        generation_properties["response_format"] = MarkdownModel

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

        return response.choices[0].message.parsed.model_dump().get("markdown")  # type: ignore

    def _generate_references(
        self,
    ) -> List[Dict[str, Any]]:
        # Get the task properties
        directory = NestedDictAccessor.get_nested_value(
            data=self.task_properties,
            key="directory",
            default=ParsingTask.DEFAULT_DIRECTORY,
        )

        file_type = NestedDictAccessor.get_nested_value(
            data=self.task_properties,
            key="file_type",
            default=ParsingTask.DEFAULT_FILE_TYPE,
        )

        max_depth = NestedDictAccessor.get_nested_value(
            data=self.task_properties,
            key="max_depth",
            default=ParsingTask.DEFAULT_MAX_DEPTH,
        )

        parsed_list = FileUtils._parse_files(directory, file_type, max_depth)
        return [
            {
                ParsingTask.EXPECTED_KEY: path,
            }
            for path in parsed_list
        ]


class ImageUtils:
    @staticmethod
    def _process_image(
        image_path: str,
        return_base64: bool = True,
    ) -> Union[List[Image.Image], List[str]]:
        """
        Processes a single image file.
        """
        image = ImageUtils._read_image_file(image_path)
        return [ImageUtils._image_to_base64(image)] if return_base64 else [image]

    @staticmethod
    def _read_image_file(
        file_path: str,
    ):
        """
        Reads an image file from the given path.
        """
        return Image.open(file_path)

    @staticmethod
    def _image_to_base64(
        image,
        format: Optional[str] = None,
    ):
        """
        Converts an image file to a base64 string.
        """
        buffered = BytesIO()
        # Use the original image format if available and no format is specified
        if format is None:
            format = image.format or "PNG"
        image.save(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def _base64_to_image(
        base64_string: str,
    ):
        """
        Converts a base64 string to an image file.
        """
        image_data = base64.b64decode(
            base64_string,
        )
        return Image.open(BytesIO(image_data))


class AudioUtils:
    @staticmethod
    def _read_audio_file(
        file_path: str,
    ):
        """
        Reads an audio file from the given path.
        """
        return AudioSegment.from_file(
            file_path,
        )

    @staticmethod
    def _audio_to_base64(
        audio,
        format: str = "mp3",
    ):
        """
        Converts an audio file to a base64 string.
        """
        buffered = BytesIO()
        audio.export(
            buffered,
            format=format,
        )
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def _base64_to_audio(
        base64_string: str,
    ):
        """
        Converts a base64 string to an audio file.
        """
        audio_data = base64.b64decode(
            base64_string,
        )
        return AudioSegment.from_file(BytesIO(audio_data))


class DocUtils:
    DPI = 300
    FMT = "png"
    SIZE = None
    THREAD_COUNT = 1
    USE_PDFTOCAIRO = False

    @staticmethod
    def _process_document(
        pdf_path: str,
        return_base64: bool = True,
        dpi: Optional[int] = None,
        fmt: Optional[str] = None,
        size: Optional[str] = None,
        thread_count: Optional[int] = None,
        use_pdftocairo: Optional[bool] = None,
    ) -> Union[List[Image.Image], List[str]]:
        """
        Processes a single PDF file.
        """

        options = {
            "dpi": dpi or DocUtils.DPI,
            "fmt": fmt or DocUtils.FMT,
            "size": size or DocUtils.SIZE,
            "thread_count": thread_count or DocUtils.THREAD_COUNT,
            "use_pdftocairo": use_pdftocairo or DocUtils.USE_PDFTOCAIRO,
        }

        try:
            images = convert_from_path(pdf_path, **options)

            if return_base64:
                return [ImageUtils._image_to_base64(img) for i, img in enumerate(images, start=1)]
            else:
                return images
        except Exception as err:
            warnings.warn(f"Error processing PDF: {err}")
            return []


class FileUtils:
    @staticmethod
    def _parse_files(
        directory: str,
        file_types: str,
        max_depth: int,
    ) -> List[str]:
        """
        Parse files in a directory and return a list of absolute file paths.
        """
        # Convert directory to absolute path
        directory = os.path.abspath(directory)

        # Parse files
        result = []

        def traverse(
            current_dir: str,
            current_depth: int,
        ):
            if current_depth > max_depth:
                return

            try:
                for entry in os.scandir(current_dir):
                    if entry.is_file():
                        _, ext = os.path.splitext(entry.name)
                        if ext[1:] == file_types:  # Remove the dot from extension
                            result.append(os.path.abspath(entry.path))
                    elif entry.is_dir():
                        traverse(entry.path, current_depth + 1)
            except PermissionError:
                warnings.warn(
                    f"Permission denied for directory: {current_dir}. Skipping this directory."
                )

        traverse(directory, 0)

        return result

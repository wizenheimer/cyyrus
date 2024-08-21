import base64
import os
import warnings
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pdf2image import convert_from_path
from PIL import Image
from pydub import AudioSegment

from cyyrus.models.task_type import TaskType
from cyyrus.tasks.base import BaseTask


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

    EXPECTED_KEY = "path"

    def execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        """
        Perform the parsing task.
        """
        path = self._get_task_input(
            ParsingTask.EXPECTED_KEY,
            task_input,
        )

        # Process the file, in this case, a PDF file
        return DocUtils._process_pdf(
            path,
        )

    def _generate_references(
        self,
    ) -> List[Dict[str, Any]]:
        # Get the task properties
        directory = self._get_task_property(
            key="directory",
            default=ParsingTask.DEFAULT_DIRECTORY,
        )
        file_type = self._get_task_property(
            key="file_type",
            default=ParsingTask.DEFAULT_FILE_TYPE,
        )
        max_depth = self._get_task_property(
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
    def read_image_file(
        file_path: str,
    ):
        """
        Reads an image file from the given path.
        """
        return Image.open(file_path)

    @staticmethod
    def image_to_base64(
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
    def base64_to_image(
        base64_string: str,
    ):
        """
        Converts a base64 string to an image file.
        """
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data))


class AudioUtils:
    @staticmethod
    def read_audio_file(
        file_path: str,
    ):
        """
        Reads an audio file from the given path.
        """
        return AudioSegment.from_file(file_path)

    @staticmethod
    def audio_to_base64(
        audio,
        format: str = "mp3",
    ):
        """
        Converts an audio file to a base64 string.
        """
        buffered = BytesIO()
        audio.export(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def base64_to_audio(
        base64_string: str,
    ):
        """
        Converts a base64 string to an audio file.
        """
        audio_data = base64.b64decode(base64_string)
        return AudioSegment.from_file(BytesIO(audio_data))


class DocUtils:
    DPI = 300
    FMT = "png"
    SIZE = None
    THREAD_COUNT = 1
    USE_PDFTOCAIRO = False

    @staticmethod
    def _process_pdf(
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
                return [ImageUtils.image_to_base64(img) for i, img in enumerate(images, start=1)]
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

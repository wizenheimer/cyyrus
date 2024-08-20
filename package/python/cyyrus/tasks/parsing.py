import base64
import os
import warnings
from io import BytesIO
from typing import Any, Dict, List, Optional, Union

from pdf2image import convert_from_path
from PIL import Image
from pydub import AudioSegment

from cyyrus.models.task_type import TaskType
from cyyrus.tasks.base import BaseTask


class ParsingTask(BaseTask):
    TASK_ID = TaskType.PARSING

    def _execute(
        self,
        task_input: Dict[str, Any],
    ) -> Any:
        return f"Default Task: {task_input} with Task Properties: {self.task_properties}"


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
    FMT = "pdf"
    SIZE = None
    THREAD_COUNT = 1
    USE_PDFTOCAIRO = True

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
        file_types: List[str],
        max_depth: int,
    ) -> List[str]:
        """
        Parse files in a directory and return a list of file paths.
        """

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
                        if ext[1:] in file_types:  # Remove the dot from extension
                            result.append(entry.path)
                    elif entry.is_dir():
                        traverse(entry.path, current_depth + 1)
            except PermissionError:
                warnings.warn(
                    f"Permission denied for directory: {current_dir}. Skipping this directory."
                )

        traverse(directory, 0)

        return result

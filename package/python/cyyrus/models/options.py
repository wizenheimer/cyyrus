from enum import Enum


class UnparsedFormat(str, Enum):
    """
    Enum for the different formats in which data can be stored before parsing.
    """

    # Document Formats
    PDF = "pdf"

    # Image Formats
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"

    # Tabular Formats
    JSON = "json"
    CSV = "csv"


class ParsedFormat(str, Enum):
    """
    Enum for the different formats in which data can be stored after parsing.
    """

    BASE64 = "base64"
    MARKDOWN = "markdown"
    IMAGE = "image"


class LargeLanguageModels(str, Enum):
    """
    Enum for the different large language models supported by the API.
    """

    GPT_4 = "gpt-4"
    GPT_4O_MINI = "gpt-4o-mini"


class VisionLanguageModels(str, Enum):
    """
    Enum for the different vision language models supported by the API.
    """

    GPT_4 = "gpt-4"
    GPT_4O_MINI = "gpt-4o-mini"

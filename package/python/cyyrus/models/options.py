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


class EmbeddingModels(str, Enum):
    """
    Enum for the different text embedding models supported by the API.
    """

    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    JINA_EMBEDDING_V2 = "jina-embedding-v2"

from enum import Enum

from cyyrus.models.options import (
    EmbeddingModels,
    LargeLanguageModels,
    ParsedFormat,
    UnparsedFormat,
)


class TaskType(str, Enum):
    # === Sentinel Tasks ===
    DEFAULT = "default"

    # === General Tasks ===
    PARSING = "parsing"  # Ingest and interpret data from different types.
    SCRAPING = "scraping"  # Collect and extract data from websites or online sources.

    # === Document Processing Tasks ===
    DOCUMENT_GENERATION = "document_generation"  # Create new documents based on given inputs.

    # === Multimodal Tasks ===
    GENERATION = (
        "generation"  # Create new content, such as generating text or audio from given inputs.
    )
    EMBEDDING = "embedding"  # Transform data into a numerical format that preserves semantic meaning (e.g., word embeddings).

    # === Text Processing Tasks ===
    CATEGORIZATION = "categorization"  # Classify text into predefined categories or labels.


# ==============================================================================
#                                   Task Properties
# ==============================================================================

TASK_PROPERTIES = {
    TaskType.DEFAULT: {
        "required": {},
        "optional": {},
    },
    TaskType.PARSING: {
        "required": {
            "directory": (
                str,
                ...,
            ),
            "file_type": (
                UnparsedFormat,
                ...,
            ),
            "max_depth": (
                int,
                5,
            ),
            "parsed_format": (
                ParsedFormat,
                ParsedFormat.BASE64,
            ),
        },
        "optional": {},
    },
    TaskType.SCRAPING: {
        "required": {
            "url": (
                str,
                ...,
            ),
            "max_depth": (int, 5),
        },
        "optional": {},
    },
    TaskType.DOCUMENT_GENERATION: {
        "required": {
            "path": (
                str,
                ...,
            ),
        },
        "optional": {},
    },
    TaskType.GENERATION: {
        "required": {
            "prompt": (str, ...),
            "model": (
                LargeLanguageModels,
                LargeLanguageModels.GPT_4O_MINI,
            ),
        },
        "optional": {},
    },
    TaskType.EMBEDDING: {
        "required": {
            "model": (
                EmbeddingModels,
                EmbeddingModels.TEXT_EMBEDDING_3_SMALL,  # TODO: add support for image embeddings
            ),
        },
        "optional": {},
    },
    TaskType.CATEGORIZATION: {
        "required": {
            "primary_model": (
                EmbeddingModels,
                EmbeddingModels.JINA_EMBEDDING_V2,
            ),
            "secondary_model": (
                LargeLanguageModels,
                LargeLanguageModels.GPT_4O_MINI,
            ),
        },
        "optional": {},
    },
}

from enum import Enum

from cyyrus.models.options import (
    ParsedFormat,
    UnparsedFormat,
)


class TaskType(str, Enum):
    # === Sentinel Tasks ===
    DEFAULT = "default"

    # === General Tasks ===
    PARSING = "parsing"  # Ingest and interpret data from different types.

    # === Multimodal Tasks ===
    GENERATION = (
        "generation"  # Create new content, such as generating text or audio from given inputs.
    )


TASK_PROPERTIES = {
    TaskType.DEFAULT: {
        "required": {},
        "optional": {},
    },
    TaskType.PARSING: {
        "required": {
            "parsed_format": (
                ParsedFormat,
                ParsedFormat.BASE64,
            ),
            "file_type": (
                UnparsedFormat,
                UnparsedFormat.PDF,
            ),
        },
        "optional": {
            "max_depth": (
                int,
                5,
            ),
            "directory": (
                str,
                "*",
            ),
        },
    },
    TaskType.GENERATION: {
        "required": {
            "prompt": (
                str,
                ...,
            ),
            "model": (
                str,
                ...,
            ),
            "api_key": (
                str,
                ...,
            ),
        },
        "optional": {
            "max_epochs": (
                int,
                100,
            ),
            "response_format": (
                str,
                None,
            ),
        },
    },
}

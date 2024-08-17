from typing import Dict
from pydantic import BaseModel, Field
from enum import Enum


class ReferenceType(str, Enum):
    DOCUMENT = "document"
    VISION = "vision"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    TABULAR = "tabular"
    URL = "url"
    ARCHIVE = "archive"
    SQL = "sql"


class Column(BaseModel):
    column_type: str = Field(..., description="Type of the column")
    description: str = Field(
        default="",
        description="Description of the column",
    )
    task_id: str = Field(
        ...,
        description="ID of the task associated with the column",
    )
    task_input: Dict[str, str] = Field(
        default={},
        description="Input to the task",
    )

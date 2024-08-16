from pydantic import BaseModel, Field
from typing import List, Union
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


class Reference(BaseModel):
    description: str = Field(
        default="",
        description="Description of the reference",
    )
    type: ReferenceType = Field(
        ...,
        description="Type of the reference",
    )
    path: Union[List[str], str] = Field(
        ...,
        description="Path to the reference",
    )

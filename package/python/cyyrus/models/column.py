from typing import List, Union

from pydantic import BaseModel, Field

from cyyrus.models.types import (
    StaticArrayModel,
    StaticBooleanModel,
    StaticFloatModel,
    StaticIntegerModel,
    StaticStringModel,
)


class Column(BaseModel):
    column_type: str = Field(
        ...,
        description="Type of the column",
    )
    description: str = Field(
        default="",
        description="Description of the column",
    )
    task_id: str = Field(
        ...,
        description="ID of the task associated with the column",
    )
    task_input: List[str] = Field(
        default=[],
        description="Input to the task",
    )
    pydantic_model: Union[
        type[BaseModel],
        StaticStringModel,
        StaticBooleanModel,
        StaticFloatModel,
        StaticIntegerModel,
        StaticArrayModel,
    ] = Field(
        default=StaticStringModel,
        exclude=True,
        description="Dynamic model created based on data inside CustomType and TaskType",
    )

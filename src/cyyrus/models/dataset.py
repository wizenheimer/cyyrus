import warnings
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum

from cyyrus.errors.schema import DatasetSplitsDontAddUpError


class SpecVersion(str, Enum):
    V0 = "v0"


class DatasetMetadata(BaseModel):
    name: str = Field(
        default="Dataset",
        description="Name of the dataset",
    )
    description: str = Field(
        default="Dataset generated using cyyrus",
        description="Description of the dataset",
    )
    tags: List[str] = Field(
        default=[
            "dataset",
        ],
        description="Tags for the dataset",
    )
    license: str = Field(
        default="MIT",
        description="License for the dataset",
    )
    language: str = Field(
        default="en",
        description="Language of the dataset",
    )


class DatasetSampling(BaseModel):
    percentage: float = Field(
        default=1,
        gt=0,
        le=1,
        description="Percentage of the dataset to sample",
    )


class DatasetShuffle(BaseModel):
    seed: int = Field(
        default=42,
        description="Seed for the random number generator",
    )
    buffer_size: int = Field(
        default=1000,
        gt=0,
        description="Buffer size for shuffling",
    )


class DatasetSplits(BaseModel):
    train: Optional[float] = Field(
        default=0.8,
        ge=0,
        le=1,
        description="Percentage of the dataset to use for training",
    )
    test: Optional[float] = Field(
        default=0.1,
        ge=0,
        le=1,
        description="Percentage of the dataset to use for testing",
    )
    validation: Optional[float] = Field(
        default=0.1,
        ge=0,
        le=1,
        description="Percentage of the dataset to use for validation",
    )

    @field_validator("test", "validation", mode="after")
    @classmethod
    def check_splits_sum(cls, v, info):
        values = info.data
        total = sum(
            filter(
                None,
                [
                    values.get("train", 0),
                    v,
                    values.get("validation" if v == values.get("test") else "test", 0),
                ],
            )
        )
        if total > 1:
            warnings.warn(DatasetSplitsDontAddUpError())
            # Normalize the splits if they don't add up to 1
            v = v / total
            values["train"] = values.get("train", 0) / total
            values["validation"] = values.get("validation", 0) / total
            values["test"] = values.get("test", 0) / total

            return v

        return v


class DatasetAttributes(BaseModel):
    required_columns: List[str] = Field(
        default=[],
        description="Columns that are required in the dataset",
    )
    unique_columns: List[str] = Field(
        default=[],
        description="Columns that are unique in the dataset",
    )
    nulls: str = Field(
        default="include",
        pattern="^(include|exclude)$",
        description="How to handle null values",
    )
    references: str = Field(
        default="include",
        pattern="^(include|exclude)$",
        description="How to handle references",
    )


class Dataset(BaseModel):
    metadata: DatasetMetadata = Field(
        default_factory=DatasetMetadata,
        description="Metadata for the dataset",
    )
    sampling: DatasetSampling = Field(
        default_factory=DatasetSampling,
        description="Sampling configuration for the dataset",
    )
    shuffle: DatasetShuffle = Field(
        default_factory=DatasetShuffle,
        description="Shuffle configuration for the dataset",
    )
    splits: DatasetSplits = Field(
        default_factory=DatasetSplits,  # type: ignore
        description="Splits for the dataset",
    )
    attributes: DatasetAttributes = Field(
        default_factory=DatasetAttributes,
        description="Attributes for the dataset",
    )

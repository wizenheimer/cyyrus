import warnings
from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator
from pydantic.functional_validators import model_validator

from cyyrus.errors.dataset import (
    SplitsDontAddUpWarning,
    SplitValueInvalidWarning,
)


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


class DatasetShuffle(BaseModel):
    seed: int = Field(
        default=42,
        description="Seed for the random number generator",
    )


class DatasetSplits(BaseModel):
    train: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Percentage of the dataset to use for training",
    )
    test: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Percentage of the dataset to use for testing",
    )
    seed: Optional[int] = Field(
        default=42,
        description="Seed for the random number generator",
    )

    @model_validator(mode="after")
    def check_splits_sum(cls, values):
        train, test = values.train, values.test

        if train is None and test is None:
            values.train, values.test = 0.8, 0.2
            warnings.warn(
                SplitValueInvalidWarning(
                    extra_info={
                        "new train split": 0.8,
                        "new test split": 0.2,
                        "old train split": train,
                        "old test split": test,
                    }
                )
            )
        elif train is None:
            values.train = max(0, 1 - test)
            warnings.warn(
                SplitValueInvalidWarning(
                    extra_info={
                        "new train split": values.train,
                        "new test split": test,
                        "old train split": train,
                        "old test split": test,
                    }
                )
            )
        elif test is None:
            values.test = max(0, 1 - train)
            warnings.warn(
                SplitValueInvalidWarning(
                    extra_info={
                        "new train split": train,
                        "new test split": values.test,
                        "old train split": train,
                        "old test split": test,
                    }
                )
            )

        normalized = cls.normalize_split_sizes(values.train, values.test)
        values.train, values.test = normalized

        return values

    @staticmethod
    def normalize_split_sizes(
        train_size: float,
        test_size: float,
    ) -> Tuple[float, float]:
        total = train_size + test_size
        if total <= 0:
            warnings.warn(
                SplitsDontAddUpWarning(
                    extra_info={
                        "new train split": 0.8,
                        "new test split": 0.2,
                        "old train split": train_size,
                        "old test split": test_size,
                    }
                )
            )
            return 0.8, 0.2
        return round(train_size / total, 3), round(test_size / total, 3)

    @field_validator("train", "test")
    @classmethod
    def check_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            warnings.warn(
                SplitValueInvalidWarning(
                    extra_info={
                        "old value": v,
                        "new value": abs(v),
                    }
                )
            )
            return abs(v)
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


class Dataset(BaseModel):
    metadata: DatasetMetadata = Field(
        default_factory=DatasetMetadata,
        description="Metadata for the dataset",
    )
    shuffle: DatasetShuffle = Field(
        default_factory=DatasetShuffle,
        description="Shuffle configuration for the dataset",
    )
    splits: DatasetSplits = Field(
        default_factory=DatasetSplits,
        description="Splits for the dataset",
    )
    attributes: DatasetAttributes = Field(
        default_factory=DatasetAttributes,
        description="Attributes for the dataset",
    )

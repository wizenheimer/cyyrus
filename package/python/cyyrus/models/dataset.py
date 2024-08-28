from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator
from pydantic.functional_validators import model_validator

from cyyrus.constants.messages import Messages
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


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
            "cyyrus",
        ],
        description="Tags for the dataset",
    )
    license: str = Field(
        default="MIT",
        description="License for the dataset",
    )
    languages: List[str] = Field(
        default=[
            "en",
        ],
        description="Languages for the dataset",
    )

    @field_validator("tags")
    @classmethod
    def add_cyyrus_tag(
        cls,
        v: List[str],
    ) -> List[str]:
        if "cyyrus" not in v:
            v.append("cyyrus")
        return v


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
        logger.debug(f"Checking splits sum: {values}")
        train, test = values.train, values.test

        if train is None and test is None:
            logger.warn(Messages.SPLITS_DONT_ADD_UP)
            logger.debug("Both train and test splits are None, attempting to set default values")

            values.train, values.test = 0.8, 0.2

            logger.debug(f"Old train split: {train}, Old test split: {test}")
            logger.debug(f"New train split: {values.train}, New test split: {values.test}")

        elif train is None:
            logger.warn(Messages.SPLIT_VALUE_INVALID)
            logger.debug(f"Train split is None, attempting to compute from test split: {test}")

            values.train = max(0, 1 - test)

            logger.debug(f"Old train split: {train}, Old test split: {test}")
            logger.debug(f"New train split: {values.train}, New test split: {values.test}")
        elif test is None:
            logger.warn(Messages.SPLIT_VALUE_INVALID)
            logger.debug("Test split is None, attempting to compute from train split")

            values.test = max(0, 1 - train)

            logger.debug(f"Old train split: {train}, Old test split: {test}")
            logger.debug(f"New train split: {values.train}, New test split: {values.test}")

        logger.debug(f"Checking splits sum: {values}, train: {train}, test: {test}")
        normalized = cls.normalize_split_sizes(values.train, values.test)

        logger.debug(f"Normalized splits: {normalized}")
        values.train, values.test = normalized

        return values

    @staticmethod
    def normalize_split_sizes(
        train_size: float,
        test_size: float,
    ) -> Tuple[float, float]:
        total = train_size + test_size
        if total <= 0:
            logger.warning(f"{Messages.SPLITS_DONT_ADD_UP}")
            logger.warning(f"Old train split: {train_size}, Old test split: {test_size}")
            logger.warning(f"New train split: {0.8}, New test split: {0.2}")
            return 0.8, 0.2
        return round(train_size / total, 3), round(test_size / total, 3)

    @field_validator("train", "test")
    @classmethod
    def check_not_negative(cls, v: Optional[float]) -> Optional[float]:
        logger.debug(f"Checking if {v} is negative")
        if v is not None and v < 0:
            logger.warning(Messages.SPLIT_VALUE_INVALID)
            logger.debug(f"Old value: {v}, New value: {abs(v)}")
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
    flatten_columns: List[str] = Field(
        default=[],
        description="Columns that should be flattened",
    )
    exclude_columns: List[str] = Field(
        default=[],
        description="Columns that should be excluded",
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

from enum import Enum
from typing import List, Tuple

import pandas as pd
from datasets import Dataset

from cyyrus.constants.messages import Messages
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


class ExportFormat(str, Enum):
    HUGGINGFACE = "huggingface"
    JSON = "json"
    CSV = "csv"
    PICKLE = "pickle"
    PARQUET = "parquet"


class DataFrameUtils:
    @staticmethod
    def handle_nulls(
        df: pd.DataFrame,
        nulls: str,
    ) -> pd.DataFrame:
        """
        Drops rows with null values if nulls is set to "exclude".
        """
        if nulls == "exclude":
            return df.dropna()
        return df

    @staticmethod
    def ensure_required_columns(
        df: pd.DataFrame,
        required_columns: List[str],
    ) -> pd.DataFrame:
        """
        Ensure that the required columns are present in the DataFrame.
        """
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            logger.warning(Messages.REQUIRED_COLUMN_MISSING)
            logger.warning(f"Missing columns: {missing_columns}")
            for col in missing_columns:
                df[col] = pd.Series(dtype=object)
        return df

    @staticmethod
    def ensure_unique_columns(
        df: pd.DataFrame,
        unique_columns: List[str],
    ) -> pd.DataFrame:
        """
        Ensure that the unique columns have unique values in the DataFrame.
        Drops duplicates if unique_columns is not empty.
        """
        if unique_columns:
            initial_count = len(df)
            df = df.drop_duplicates(subset=unique_columns, keep="first")
            removed_count = initial_count - len(df)
            if removed_count > 0:
                logger.warning(Messages.NON_UNIQUE_COLUMN_VALUES)
                logger.warning(f"Unique columns: {unique_columns}, Removed count: {removed_count}")
        return df


class DatasetUtils:
    @staticmethod
    def normalize_split_sizes(
        train_size: float,
        test_size: float,
    ) -> Tuple[float, float]:
        """
        Normalize the split sizes to ensure they add up to 1.
        """
        logger.debug(f"Validating splits: train: {train_size}, test: {test_size}")
        total = train_size + test_size
        if total <= 0:
            logger.debug(f"Old train split: {train_size}, Old test split: {test_size}")
            logger.debug("New train split: 1, New test split: 0")
            return 1.0, 0.0
        if train_size < 0:
            logger.debug(f"Old train split: {train_size}, Old test split: {test_size}")
            logger.debug("New train split: 0")
            train_size = 0
        if test_size < 0:
            logger.debug(f"Old train split: {train_size}, Old test split: {test_size}")
            logger.debug("New test split: 0")
            test_size = 0
        if abs(total - 1) > 1e-6:
            logger.warning(Messages.SPLITS_DONT_ADD_UP)
            logger.debug(f"Old train split: {train_size}, Old test split: {test_size}")
            logger.debug(
                f"New train split: {train_size / total}, New test split: {test_size / total}"
            )
            logger.debug(f"Normalizing splits: train: {train_size}, test: {test_size}")
            return train_size / total, test_size / total

        logger.debug(f"Final splits: train: {train_size}, test: {test_size}")
        return train_size, test_size

    @staticmethod
    def split_dataset(
        dataset: Dataset,
        train_size: float,
        test_size: float,
        seed: int,
    ) -> Tuple[Dataset, Dataset]:
        """
        Splits the dataset into train and test sets.
        """
        logger.debug(f"Splitting dataset with sizes: train: {train_size}, test: {test_size}")
        total_size = len(dataset)

        # Normalize split sizes
        train_size, test_size = DatasetUtils.normalize_split_sizes(
            train_size,
            test_size,
        )

        # Ensure at least one sample in each split
        min_samples = 1
        if total_size < 2 * min_samples:
            logger.warning(Messages.DATASET_TOO_SMALL_FOR_SPLIT)
            logger.warning(f"Total size: {total_size}, min samples: {min_samples}")
            return dataset, Dataset.from_dict({})

        train_samples = max(min_samples, int(total_size * train_size))
        test_samples = max(min_samples, total_size - train_samples)

        if train_samples + test_samples > total_size:
            logger.warning(Messages.RE_ADJUSTING_SPLIT)
            logger.warning(
                f"Train samples: {train_samples}, Test samples: {test_samples}, Total size: {total_size}"
            )
            if train_samples > test_samples:
                train_samples = total_size - min_samples
                test_samples = min_samples
            else:
                test_samples = total_size - min_samples
                train_samples = min_samples

        # Perform the split
        logger.debug(f"Performing dataset split {train_samples} train, {test_samples} test")
        split = dataset.train_test_split(
            train_size=train_samples, test_size=test_samples, seed=seed
        )
        return split["train"], split["test"]

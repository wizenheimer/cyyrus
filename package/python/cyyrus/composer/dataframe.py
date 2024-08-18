import warnings
from typing import List, Tuple

import pandas as pd
from datasets import Dataset

from cyyrus.errors.composer import (
    DatasetTooSmallForSplitWarning,
    NonUniqueColumnValuesWarning,
    ReAdjustingSplitWarning,
    RequiredColumnMissingWarning,
)
from cyyrus.errors.dataset import SplitsDontAddUpWarning


def handle_nulls(
    df: pd.DataFrame,
    nulls: str,
) -> pd.DataFrame:
    if nulls == "exclude":
        return df.dropna()
    return df


def ensure_required_columns(
    df: pd.DataFrame,
    required_columns: List[str],
) -> pd.DataFrame:
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        warnings.warn(
            RequiredColumnMissingWarning(
                extra_info={
                    "missing_columns": list(missing_columns),
                }
            )
        )
        for col in missing_columns:
            df[col] = pd.Series(dtype=object)
    return df


def ensure_unique_columns(
    df: pd.DataFrame,
    unique_columns: List[str],
) -> pd.DataFrame:
    if unique_columns:
        initial_count = len(df)
        df = df.drop_duplicates(subset=unique_columns, keep="first")
        removed_count = initial_count - len(df)
        if removed_count > 0:
            warnings.warn(
                NonUniqueColumnValuesWarning(
                    extra_info={
                        "unique_columns": unique_columns,
                        "removed_count": removed_count,
                    }
                )
            )
    return df


def normalize_split_sizes(
    train_size: float,
    test_size: float,
) -> Tuple[float, float]:
    total = train_size + test_size
    if total <= 0:
        warnings.warn(
            SplitsDontAddUpWarning(
                extra_info={
                    "new train split": 1,
                    "new test split": 0,
                    "old train split": train_size,
                    "old test split": test_size,
                }
            )
        )
        return 1.0, 0.0
    if train_size < 0:
        warnings.warn(
            SplitsDontAddUpWarning(
                extra_info={
                    "new train split": 0,
                    "new test split": 0,
                    "old train split": train_size,
                    "old test split": test_size,
                }
            )
        )
        train_size = 0
    if test_size < 0:
        warnings.warn(
            SplitsDontAddUpWarning(
                extra_info={
                    "new train split": 0,
                    "new test split": 0,
                    "old train split": train_size,
                    "old test split": test_size,
                }
            )
        )
        test_size = 0
    if abs(total - 1) > 1e-6:
        warnings.warn(
            SplitsDontAddUpWarning(
                extra_info={
                    "new train split": train_size / total,
                    "new test split": test_size / total,
                    "old train split": train_size,
                    "old test split": test_size,
                }
            )
        )
        return train_size / total, test_size / total
    return train_size, test_size


def split_dataset(
    dataset: Dataset,
    train_size: float,
    test_size: float,
    seed: int,
) -> Tuple[Dataset, Dataset]:
    total_size = len(dataset)

    # Normalize split sizes
    train_size, test_size = normalize_split_sizes(train_size, test_size)

    # Ensure at least one sample in each split
    min_samples = 1
    if total_size < 2 * min_samples:
        warnings.warn(
            DatasetTooSmallForSplitWarning(
                extra_info={
                    "total_size": total_size,
                    "min_samples": min_samples,
                }
            )
        )
        return dataset, Dataset.from_dict({})

    train_samples = max(min_samples, int(total_size * train_size))
    test_samples = max(min_samples, total_size - train_samples)

    if train_samples + test_samples > total_size:
        warnings.warn(
            ReAdjustingSplitWarning(
                extra_info={
                    "train_samples": train_samples,
                    "test_samples": test_samples,
                    "total_size": total_size,
                }
            )
        )
        if train_samples > test_samples:
            train_samples = total_size - min_samples
            test_samples = min_samples
        else:
            test_samples = total_size - min_samples
            train_samples = min_samples

    # Perform the split
    split = dataset.train_test_split(train_size=train_samples, test_size=test_samples, seed=seed)
    return split["train"], split["test"]

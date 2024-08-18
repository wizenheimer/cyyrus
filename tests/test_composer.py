import pandas as pd
import pytest
from cyyrus.composer.dataframe import (  # type: ignore
    ensure_required_columns,
    ensure_unique_columns,
    handle_nulls,
    normalize_split_sizes,
    split_dataset,
)
from datasets import Dataset


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "A": [1, 2, 3, None, 5],
            "B": ["a", "b", "c", "d", "e"],
            "C": [1.1, 2.2, 3.3, 4.4, 5.5],
        }
    )


def test_handle_nulls(sample_df):
    # Test include nulls
    result = handle_nulls(sample_df, "include")
    assert len(result) == len(sample_df)

    # Test exclude nulls
    result = handle_nulls(sample_df, "exclude")
    assert len(result) == len(sample_df) - 1


def test_ensure_required_columns(sample_df):
    with pytest.warns():
        result = ensure_required_columns(sample_df, ["A", "B", "D"])
    assert "D" in result.columns
    assert result["D"].isnull().all()


def test_ensure_unique_columns(sample_df):
    df_with_duplicates = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
    with pytest.warns():
        result = ensure_unique_columns(df_with_duplicates, ["B"])
    assert len(result) == len(sample_df)


def test_normalize_split_sizes():
    # Test normal case
    train, test = normalize_split_sizes(0.8, 0.2)
    assert train == 0.8 and test == 0.2

    # Test case where sum != 1
    with pytest.warns():
        train, test = normalize_split_sizes(0.8, 0.3)
    assert pytest.approx(train + test) == 1


def test_split_dataset():
    dataset = Dataset.from_pandas(pd.DataFrame({"A": range(100)}))
    train, test = split_dataset(dataset, 0.8, 0.2, 42)
    assert len(train) == 80
    assert len(test) == 20

    # Test with extreme values
    train, test = split_dataset(dataset, 0.999, 0.001, 42)
    assert len(train) >= 1
    assert len(test) >= 1

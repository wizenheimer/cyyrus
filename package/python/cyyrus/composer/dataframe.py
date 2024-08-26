from enum import Enum
from typing import List

import pandas as pd

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

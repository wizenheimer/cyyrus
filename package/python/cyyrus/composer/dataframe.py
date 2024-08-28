from enum import Enum
from typing import Any, Dict, List

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

    @staticmethod
    def handle_flattening(
        df: pd.DataFrame,
        columns_to_flatten: List[str],
    ) -> pd.DataFrame:
        """
        Robustly flatten specified dictionary columns in a DataFrame.

        Args:
        df (pd.DataFrame): The input DataFrame.
        columns_to_flatten (list): List of column names containing dictionaries to flatten.

        Returns:
        pd.DataFrame: A new DataFrame with specified dictionary columns flattened.
        """
        df = df.copy()
        flattened_columns = []

        for col in columns_to_flatten:
            if col not in df.columns:
                logger.debug(f"Warning: Column '{col}' not found in the DataFrame. Skipping.")
                continue

            if not df[col].dtype == "object":
                logger.debug(f"Warning: Column '{col}' is not of object type. Skipping.")
                continue

            # Check if the column contains dictionaries
            if not df[col].apply(lambda x: isinstance(x, dict)).all():
                logger.debug(
                    f"Warning: Column '{col}' does not contain only dictionaries. Skipping."
                )
                continue

            try:
                # Flatten the dictionary column
                flattened = pd.json_normalize(df[col].apply(lambda x: x or {}))  # type: ignore

                # Rename the new columns to avoid conflicts
                flattened.columns = [f"{col}_{key}" for key in flattened.columns]

                # Add the flattened columns to our list
                flattened_columns.append(flattened)

                # Drop the original column
                df = df.drop(columns=[col])
            except Exception as e:
                logger.debug(f"Error flattening column '{col}': {str(e)}. Skipping.")

        # Concatenate all flattened columns with the original DataFrame
        if flattened_columns:
            df = pd.concat([df] + flattened_columns, axis=1)

        return df

    # Helper function to safely get nested dictionary values
    @staticmethod
    def safe_get(
        dct: Dict[str, Any],
        *keys: str,
    ) -> Any:
        for key in keys:
            try:
                dct = dct[key]
            except (KeyError, TypeError):
                return None
        return dct

    @staticmethod
    def remove_columns(
        df: pd.DataFrame,
        columns_to_remove: List[str],
    ) -> pd.DataFrame:
        """
        Remove specified columns from a DataFrame if they exist.

        Args:
        df (pd.DataFrame): The input DataFrame.
        columns_to_remove (List[str]): List of column names to remove.

        Returns:
        pd.DataFrame: A new DataFrame with specified columns removed.
        """
        df = df.copy()
        existing_columns = df.columns.tolist()

        for col in columns_to_remove:
            if col in existing_columns:
                df = df.drop(columns=[col])
                logger.debug(f"Removed column: '{col}'")
            else:
                logger.debug(f"Column '{col}' not found in the DataFrame. Skipping.")

        return df

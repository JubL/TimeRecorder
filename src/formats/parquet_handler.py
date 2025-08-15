"""
Parquet format handler for TimeRecorder.

This module provides Parquet-specific implementation for reading and writing
timereport_logbook data.
"""

from pathlib import Path

import pandas as pd

from .base import BaseFormatHandler


class ParquetHandler(BaseFormatHandler):
    """
    Parquet format handler for TimeRecorder logbook data.

    Handles reading and writing Parquet files for efficient storage.
    """

    @staticmethod
    def load(file_path: Path) -> pd.DataFrame:
        """
        Load data from a Parquet file into a pandas DataFrame.

        Parameters
        ----------
        file_path : Path
            Path to the Parquet file to load.

        Returns
        -------
        pd.DataFrame
            Loaded data as a DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist.
        ValueError
            If the Parquet format is invalid.
        """
        try:
            return pd.read_parquet(file_path)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Parquet file not found: {file_path}") from e
        except Exception as e:
            raise ValueError(f"Error reading Parquet file {file_path}: {e}") from e

    @staticmethod
    def save(df: pd.DataFrame, file_path: Path) -> None:
        """
        Save a pandas DataFrame to a Parquet file.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to save.
        file_path : Path
            Path where to save the Parquet file.

        Raises
        ------
        PermissionError
            If the file cannot be written due to permissions.
        OSError
            If there's an OS-level error during writing.
        """
        try:
            df.to_parquet(file_path, index=False)

        except PermissionError as e:
            raise PermissionError(f"Permission denied when saving Parquet to {file_path}: {e}") from e
        except OSError as e:
            raise OSError(f"OS error while saving Parquet to {file_path}: {e}") from e

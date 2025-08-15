"""
CSV format handler for TimeRecorder.

This module provides CSV-specific implementation for reading and writing
timereport_logbook data.
"""

from pathlib import Path

import pandas as pd

from .base import BaseFormatHandler


class CSVHandler(BaseFormatHandler):
    """
    CSV format handler for TimeRecorder logbook data.

    Handles reading and writing CSV files with semicolon separator and UTF-8 encoding.
    """

    def load(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from a CSV file into a pandas DataFrame.

        Parameters
        ----------
        file_path : Path
            Path to the CSV file to load.

        Returns
        -------
        pd.DataFrame
            Loaded data as a DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist.
        pd.errors.EmptyDataError
            If the file is empty.
        pd.errors.ParserError
            If the CSV format is invalid.
        """
        try:
            return pd.read_csv(file_path, sep=";", keep_default_na=False, encoding="utf-8")
        except pd.errors.EmptyDataError as e:
            raise pd.errors.EmptyDataError(f"CSV file is empty: {file_path}") from e
        except pd.errors.ParserError as e:
            raise pd.errors.ParserError(f"Error parsing CSV file: {file_path}") from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f"CSV file not found: {file_path}") from e

    def save(self, df: pd.DataFrame, file_path: Path) -> None:
        """
        Save a pandas DataFrame to a CSV file.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to save.
        file_path : Path
            Path where to save the CSV file.

        Raises
        ------
        PermissionError
            If the file cannot be written due to permissions.
        OSError
            If there's an OS-level error during writing.
        """
        try:
            df.to_csv(file_path, sep=";", index=False, encoding="utf-8")
        except PermissionError as e:
            raise PermissionError(f"Permission denied when saving CSV to {file_path}: {e}") from e
        except OSError as e:
            raise OSError(f"OS error while saving CSV to {file_path}: {e}") from e

    def create_empty(self, file_path: Path, columns: list[str]) -> None:
        """
        Create an empty CSV file with the correct column structure.

        Parameters
        ----------
        file_path : Path
            Path where to create the empty CSV file.
        """
        df = pd.DataFrame(columns=columns)
        self.save(df, file_path)

"""
Excel format handler for TimeRecorder.

This module provides Excel-specific implementation for reading and writing
timereport_logbook data.
"""

from pathlib import Path

import pandas as pd

from .base import BaseFormatHandler


class ExcelHandler(BaseFormatHandler):
    """
    Excel format handler for TimeRecorder logbook data.

    Handles reading and writing Excel files (.xlsx, .xls) with proper formatting.
    """

    @staticmethod
    def load(file_path: Path) -> pd.DataFrame:
        """
        Load data from an Excel file into a pandas DataFrame.

        Parameters
        ----------
        file_path : Path
            Path to the Excel file to load.

        Returns
        -------
        pd.DataFrame
            Loaded data as a DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist.
        ValueError
            If the Excel format is invalid.
        """
        try:
            # Read Excel file - pandas will automatically detect the format
            return pd.read_excel(file_path, engine="openpyxl")

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Excel file not found: {file_path}") from e
        except ImportError as e:
            raise ValueError("openpyxl library not installed. Install with: pip install openpyxl") from e
        except Exception as e:
            raise ValueError(f"Invalid Excel format in {file_path}: {e}") from e

    @staticmethod
    def save(df: pd.DataFrame, file_path: Path) -> None:
        """
        Save a pandas DataFrame to an Excel file.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to save.
        file_path : Path
            Path where to save the Excel file.

        Raises
        ------
        PermissionError
            If the file cannot be written due to permissions.
        OSError
            If there's an OS-level error during writing.
        """
        try:
            # Save DataFrame to Excel file
            # Use openpyxl engine for .xlsx files
            df.to_excel(file_path, index=False, engine="openpyxl")

        except PermissionError as e:
            raise PermissionError(f"Permission denied when saving Excel file to {file_path}: {e}") from e
        except OSError as e:
            raise OSError(f"OS error while saving Excel file to {file_path}: {e}") from e
        except ImportError as e:
            raise OSError("openpyxl library not installed. Install with: pip install openpyxl") from e

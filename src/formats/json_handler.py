"""
JSON format handler for TimeRecorder.

This module provides JSON-specific implementation for reading and writing
timereport_logbook data.
"""

import json
from pathlib import Path

import pandas as pd

from .base import BaseFormatHandler


class JSONHandler(BaseFormatHandler):
    """
    JSON format handler for TimeRecorder logbook data.

    Handles reading and writing JSON files with proper encoding.
    """

    @staticmethod
    def load(file_path: Path) -> pd.DataFrame:
        """
        Load data from a JSON file into a pandas DataFrame.

        Parameters
        ----------
        file_path : Path
            Path to the JSON file to load.

        Returns
        -------
        pd.DataFrame
            Loaded data as a DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist.
        ValueError
            If the JSON format is invalid.
        """
        try:
            with file_path.open(encoding="utf-8") as f:
                data = json.load(f)

            # Handle both list of records and records object format
            if isinstance(data, dict) and "records" in data:
                records = data["records"]
            elif isinstance(data, list):
                records = data
            else:
                raise ValueError(f"Invalid JSON structure in {file_path}")

            return pd.DataFrame(records)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"JSON file not found: {file_path}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {file_path}: {e}") from e

    @staticmethod
    def save(df: pd.DataFrame, file_path: Path) -> None:
        """
        Save a pandas DataFrame to a JSON file.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to save.
        file_path : Path
            Path where to save the JSON file.

        Raises
        ------
        PermissionError
            If the file cannot be written due to permissions.
        OSError
            If there's an OS-level error during writing.
        """
        try:
            # Convert DataFrame to records format for better JSON structure
            records = df.to_dict("records")
            data = {"records": records}

            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except PermissionError as e:
            raise PermissionError(f"Permission denied when saving JSON to {file_path}: {e}") from e
        except OSError as e:
            raise OSError(f"OS error while saving JSON to {file_path}: {e}") from e

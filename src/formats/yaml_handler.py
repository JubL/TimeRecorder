"""
YAML format handler for TimeRecorder.

This module provides YAML-specific implementation for reading and writing
timereport_logbook data.
"""

from pathlib import Path

import pandas as pd
import yaml

from .base import BaseFormatHandler


class YAMLHandler(BaseFormatHandler):
    """
    YAML format handler for TimeRecorder logbook data.

    Handles reading and writing YAML files with proper encoding.
    """

    @staticmethod
    def load(file_path: Path) -> pd.DataFrame:
        """
        Load data from a YAML file into a pandas DataFrame.

        Parameters
        ----------
        file_path : Path
            Path to the YAML file to load.

        Returns
        -------
        pd.DataFrame
            Loaded data as a DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist.
        ValueError
            If the YAML format is invalid.
        """
        try:
            with file_path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Handle both list of records and records object format
            if isinstance(data, dict) and "records" in data:
                records = data["records"]
            elif isinstance(data, list):
                records = data
            else:
                raise ValueError(f"Invalid YAML structure in {file_path}")

            return pd.DataFrame(records)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"YAML file not found: {file_path}") from e
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {file_path}: {e}") from e

    @staticmethod
    def save(df: pd.DataFrame, file_path: Path) -> None:
        """
        Save a pandas DataFrame to a YAML file.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to save.
        file_path : Path
            Path where to save the YAML file.

        Raises
        ------
        PermissionError
            If the file cannot be written due to permissions.
        OSError
            If there's an OS-level error during writing.
        """
        try:
            # Convert DataFrame to records format for better YAML structure
            data = {"columns": df.columns.tolist(), "records": df.to_dict(orient="records")}

            with file_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False, allow_unicode=True)

        except PermissionError as e:
            raise PermissionError(f"Permission denied when saving YAML to {file_path}: {e}") from e
        except OSError as e:
            raise OSError(f"OS error while saving YAML to {file_path}: {e}") from e

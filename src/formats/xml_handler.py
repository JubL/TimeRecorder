"""
XML format handler for TimeRecorder.

This module provides XML-specific implementation for reading and writing
timereport_logbook data.
"""

from pathlib import Path

import pandas as pd

from .base import BaseFormatHandler


class XMLHandler(BaseFormatHandler):
    """
    XML format handler for TimeRecorder logbook data.

    Handles reading and writing XML files with proper encoding.
    """

    @staticmethod
    def load(file_path: Path) -> pd.DataFrame:
        """
        Load data from an XML file into a pandas DataFrame.

        Parameters
        ----------
        file_path : Path
            Path to the XML file to load.

        Returns
        -------
        pd.DataFrame
            Loaded data as a DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist.
        ValueError
            If the XML format is invalid.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"XML file not found: {file_path}")

        try:
            df = pd.read_xml(file_path)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Invalid XML format in {file_path}: {e}") from e

        return df

    @staticmethod
    def save(df: pd.DataFrame, file_path: Path) -> None:
        """
        Save a pandas DataFrame to an XML file.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to save.
        file_path : Path
            Path where to save the XML file.

        Raises
        ------
        PermissionError
            If the file cannot be written due to permissions.
        OSError
            If there's an OS-level error during writing.
        """
        try:
            xml_data = df.to_xml(index=False, root_name="logbook", row_name="record")
            with file_path.open("w", encoding="utf-8") as f:
                f.write(xml_data)
        except PermissionError as e:
            raise PermissionError(f"Permission denied when saving XML to {file_path}: {e}") from e
        except OSError as e:
            raise OSError(f"OS error while saving XML to {file_path}: {e}") from e

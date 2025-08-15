"""
Base format handler for TimeRecorder file formats.

This module defines the abstract base class that all format handlers must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class BaseFormatHandler(ABC):
    """
    Abstract base class for format handlers.

    All format handlers must implement the load and save methods.
    This ensures consistent interface across different file formats.
    """

    @abstractmethod
    def load(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from a file into a pandas DataFrame.

        Parameters
        ----------
        file_path : Path
            Path to the file to load.

        Returns
        -------
        pd.DataFrame
            Loaded data as a DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist.
        ValueError
            If the file format is invalid or corrupted.
        """

    @abstractmethod
    def save(self, df: pd.DataFrame, file_path: Path) -> None:
        """
        Save a pandas DataFrame to a file.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to save.
        file_path : Path
            Path where to save the file.

        Raises
        ------
        PermissionError
            If the file cannot be written due to permissions.
        OSError
            If there's an OS-level error during writing.
        """

    @abstractmethod
    def create_empty(self, file_path: Path, columns: list[str]) -> None:
        """
        Create an empty file with the correct format structure.

        Parameters
        ----------
        file_path : Path
            Path where to create the empty file.
        """

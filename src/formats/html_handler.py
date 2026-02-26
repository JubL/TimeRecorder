"""
HTML format handler for TimeRecorder.

This module provides HTML-specific implementation for reading and writing
timereport_logbook data.
"""

from pathlib import Path

import pandas as pd

from .base import BaseFormatHandler


class HTMLHandler(BaseFormatHandler):
    """
    HTML format handler for TimeRecorder logbook data.

    Handles reading and writing HTML files with proper encoding.
    Produces a viewable HTML document with the logbook data as a table.
    """

    @staticmethod
    def load(file_path: Path) -> pd.DataFrame:
        """
        Load data from an HTML file into a pandas DataFrame.

        Parameters
        ----------
        file_path : Path
            Path to the HTML file to load.

        Returns
        -------
        pd.DataFrame
            Loaded data as a DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist.
        ValueError
            If the HTML format is invalid or contains no tables.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"HTML file not found: {file_path}")

        try:
            tables = pd.read_html(file_path, encoding="utf-8", flavor="lxml")
            if not tables:
                raise ValueError(f"No HTML tables found in {file_path}")
            return tables[0]
        except ValueError as e:
            raise ValueError(f"Invalid HTML format in {file_path}: {e}") from e

    @staticmethod
    def save(df: pd.DataFrame, file_path: Path) -> None:
        """
        Save a pandas DataFrame to an HTML file.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to save.
        file_path : Path
            Path where to save the HTML file.

        Raises
        ------
        PermissionError
            If the file cannot be written due to permissions.
        OSError
            If there's an OS-level error during writing.
        """
        try:
            table_html = df.to_html(index=False, float_format="%.2f", justify="left")
            html_content = (
                '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
                '<meta charset="utf-8">\n'
                "<title>TimeRecorder Logbook</title>\n"
                "<style>tbody td { text-align: right; }</style>\n"
                "</head>\n<body>\n"
                f"{table_html}\n"
                "</body>\n</html>"
            )
            file_path.write_text(html_content, encoding="utf-8")
        except PermissionError as e:
            raise PermissionError(f"Permission denied when saving HTML to {file_path}: {e}") from e
        except OSError as e:
            raise OSError(f"OS error while saving HTML to {file_path}: {e}") from e

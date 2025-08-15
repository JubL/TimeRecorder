"""
Formats module for handling different file formats in TimeRecorder.

This module provides a flexible and extensible system for reading and writing
timereport_logbook data in various formats (CSV, JSON, YAML, Parquet, etc.)
using the Strategy Pattern and a Format Registry.
"""

from pathlib import Path

from .base import BaseFormatHandler
from .csv_handler import CSVHandler

# from .json_handler import JSONHandler
# from .parquet_handler import ParquetHandler
from .yaml_handler import YAMLHandler

# Format registry - maps file extensions to handler classes
FORMAT_REGISTRY: dict[str, type[BaseFormatHandler]] = {
    ".txt": CSVHandler,
    ".csv": CSVHandler,
    # ".json": JSONHandler,
    ".yaml": YAMLHandler,
    ".yml": YAMLHandler,
    # ".parquet": ParquetHandler,
    # ".pq": ParquetHandler,
}


def get_format_handler(file_path: Path) -> BaseFormatHandler:
    """
    Get the appropriate format handler for the given file path.

    Parameters
    ----------
    file_path : Path
        Path to the file to determine format for.

    Returns
    -------
    BaseFormatHandler
        The appropriate format handler instance.

    Raises
    ------
    ValueError
        If the file extension is not supported.
    """
    extension = file_path.suffix.lower()

    if extension not in FORMAT_REGISTRY:
        supported_formats = ", ".join(FORMAT_REGISTRY.keys())
        raise ValueError(f"Unsupported file format: {extension}. Supported formats: {supported_formats}")

    handler_class = FORMAT_REGISTRY[extension]
    return handler_class()


def get_supported_formats() -> list[str]:
    """
    Get list of supported file format extensions.

    Returns
    -------
    list[str]
        List of supported file extensions
    """
    return list(FORMAT_REGISTRY.keys())

"""
Format registry and lookup helpers.

Maps file extensions to format handler classes and provides
get_format_handler and get_supported_formats for use by the formats package.
"""

from pathlib import Path

from .base import BaseFormatHandler
from .csv_handler import CSVHandler
from .excel_handler import ExcelHandler
from .html_handler import HTMLHandler
from .json_handler import JSONHandler
from .parquet_handler import ParquetHandler
from .xml_handler import XMLHandler
from .yaml_handler import YAMLHandler

# Format registry - maps file extensions to handler classes
FORMAT_REGISTRY: dict[str, type[BaseFormatHandler]] = {
    ".csv": CSVHandler,
    ".dat": CSVHandler,
    ".txt": CSVHandler,
    ".xls": ExcelHandler,
    ".xlsx": ExcelHandler,
    ".html": HTMLHandler,
    ".json": JSONHandler,
    ".parquet": ParquetHandler,
    ".pq": ParquetHandler,
    ".xml": XMLHandler,
    ".yaml": YAMLHandler,
    ".yml": YAMLHandler,
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

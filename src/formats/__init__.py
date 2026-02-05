"""
Formats module for handling different file formats in TimeRecorder.

This module provides a flexible and extensible system for reading and writing
timereport_logbook data in various formats (CSV, JSON, YAML, Parquet, etc.)
using the Strategy Pattern and a Format Registry.
"""

from .registry import FORMAT_REGISTRY, get_format_handler, get_supported_formats

__all__ = ["FORMAT_REGISTRY", "get_format_handler", "get_supported_formats"]

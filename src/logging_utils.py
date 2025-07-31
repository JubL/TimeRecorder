"""
Logging utilities for the TimeRecorder project.

Provides common logging formatters and configuration utilities.
"""

import logging


class LevelSpecificFormatter(logging.Formatter):
    """Custom formatter that provides different formats for different log levels."""

    def __init__(self) -> None:
        super().__init__()
        self.formatters = {
            logging.DEBUG: logging.Formatter(
                "%(levelname)s - %(funcName)s in line %(lineno)s - %(message)s",
            ),
            logging.INFO: logging.Formatter("%(message)s"),
            logging.WARNING: logging.Formatter(
                "%(levelname)s: %(message)s",
            ),
            logging.ERROR: logging.Formatter(
                "%(levelname)s: %(funcName)s - %(message)s",
            ),
            logging.CRITICAL: logging.Formatter(
                "%(levelname)s: %(funcName)s in %(filename)s:%(lineno)s - %(message)s",
            ),
        }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record using level-specific formatter."""
        formatter = self.formatters.get(record.levelno, self.formatters[logging.INFO])
        return formatter.format(record)

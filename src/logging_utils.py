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


def setup_logger(name: str, level: int = None) -> logging.Logger:
    """Set up a logger with the standard configuration.

    Parameters
    ----------
    name : str
        The name of the logger (usually __name__)
    level : int, optional
        The logging level. If None, uses the root logger's level.

    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handler if it doesn't already exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(LevelSpecificFormatter())
        logger.addHandler(handler)

    # Set level if provided, otherwise inherit from root logger
    if level is not None:
        logger.setLevel(level)

    return logger


def set_global_log_level(level: int) -> None:
    """Set the global log level for all loggers in the application.

    Parameters
    ----------
    level : int
        The logging level to set (e.g., logging.DEBUG, logging.INFO, logging.WARNING)
    """
    # Get the root logger and set its level
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Also set the level for all existing loggers
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

"""Tests for the logging utilities module."""

import logging

import pytest

import src.logging_utils as lu


@pytest.mark.fast
def test_setup_logger_basic() -> None:
    """Test basic logger setup without level specification."""
    logger_name = "test_logger"
    logger = lu.setup_logger(logger_name)

    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert isinstance(logger.handlers[0].formatter, lu.LevelSpecificFormatter)


@pytest.mark.fast
def test_setup_logger_with_level() -> None:
    """Test logger setup with specific level."""
    logger_name = "test_logger_with_level"
    level = logging.DEBUG
    logger = lu.setup_logger(logger_name, level)

    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
    assert logger.level == level
    assert len(logger.handlers) == 1


@pytest.mark.fast
def test_setup_logger_existing_logger() -> None:
    """Test that setup_logger doesn't add duplicate handlers to existing logger."""
    logger_name = "test_existing_logger"

    # Create logger first time
    logger1 = lu.setup_logger(logger_name)
    handler_count_1 = len(logger1.handlers)

    # Setup same logger again
    logger2 = lu.setup_logger(logger_name)
    handler_count_2 = len(logger2.handlers)

    # Should be the same logger instance
    assert logger1 is logger2
    # Should not have added duplicate handlers
    assert handler_count_1 == handler_count_2


@pytest.mark.fast
def test_setup_logger_different_levels() -> None:
    """Test that setup_logger can set different levels for same logger."""
    logger_name = "test_level_logger"

    # Setup with DEBUG level
    logger1 = lu.setup_logger(logger_name, logging.DEBUG)
    assert logger1.level == logging.DEBUG

    # Setup same logger with INFO level
    logger2 = lu.setup_logger(logger_name, logging.INFO)
    assert logger2.level == logging.INFO
    assert logger1 is logger2  # Same logger instance


@pytest.mark.fast
def test_setup_logger_none_level() -> None:
    """Test that setup_logger handles None level correctly."""
    logger_name = "test_none_level_logger"
    logger = lu.setup_logger(logger_name, None)

    assert isinstance(logger, logging.Logger)
    # When level is None, logger level should be NOTSET (0)
    assert logger.level == logging.NOTSET


@pytest.mark.fast
def test_setup_logger_handler_formatter() -> None:
    """Test that the handler has the correct formatter."""
    logger_name = "test_formatter_logger"
    logger = lu.setup_logger(logger_name)

    handler = logger.handlers[0]
    assert isinstance(handler.formatter, lu.LevelSpecificFormatter)

"""Tests for the logging utilities module."""

import logging
from unittest.mock import patch

import pytest

import src.logging_utils as lu


@pytest.mark.fast
def test_set_global_log_level_root_logger() -> None:
    """Test that set_global_log_level sets the root logger level."""
    original_level = logging.getLogger().level

    try:
        lu.set_global_log_level(logging.DEBUG)
        assert logging.getLogger().level == logging.DEBUG

        lu.set_global_log_level(logging.INFO)
        assert logging.getLogger().level == logging.INFO
    finally:
        # Restore original level
        logging.getLogger().setLevel(original_level)


@pytest.mark.fast
def test_set_global_log_level_existing_loggers() -> None:
    """Test that set_global_log_level sets level for existing loggers."""
    # Create some test loggers
    test_logger1 = logging.getLogger("test_global_1")
    test_logger2 = logging.getLogger("test_global_2")

    # Set initial levels
    test_logger1.setLevel(logging.WARNING)
    test_logger2.setLevel(logging.ERROR)

    try:
        # Set global level
        lu.set_global_log_level(logging.DEBUG)

        # Check that existing loggers have the new level
        assert test_logger1.level == logging.DEBUG
        assert test_logger2.level == logging.DEBUG
    finally:
        # Clean up
        logging.getLogger().setLevel(logging.WARNING)


@pytest.mark.fast
def test_set_global_log_level_all_levels() -> None:
    """Test that set_global_log_level works with all standard levels."""
    original_level = logging.getLogger().level

    try:
        levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]

        for level in levels:
            lu.set_global_log_level(level)
            assert logging.getLogger().level == level
    finally:
        # Restore original level
        logging.getLogger().setLevel(original_level)


@pytest.mark.fast
def test_set_global_log_level_with_mock() -> None:
    """Test set_global_log_level with mocked loggers."""
    with patch("logging.getLogger") as mock_get_logger:
        mock_root_logger = mock_get_logger.return_value
        mock_root_logger.manager.loggerDict = {
            "logger1": logging.getLogger("logger1"),
            "logger2": logging.getLogger("logger2"),
        }

        lu.set_global_log_level(logging.INFO)

        # Verify root logger level was set
        mock_root_logger.setLevel.assert_called_with(logging.INFO)

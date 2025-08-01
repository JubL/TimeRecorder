"""Tests for the logging utilities module."""

import logging
from unittest.mock import patch

import pytest

import src.logging_utils as lu


class TestLevelSpecificFormatter:
    """Test the LevelSpecificFormatter class."""

    def test_formatter_initialization(self) -> None:
        """Test that LevelSpecificFormatter initializes with correct formatters."""
        formatter = lu.LevelSpecificFormatter()

        # Check that all expected formatters are present
        assert logging.DEBUG in formatter.formatters
        assert logging.INFO in formatter.formatters
        assert logging.WARNING in formatter.formatters
        assert logging.ERROR in formatter.formatters
        assert logging.CRITICAL in formatter.formatters

        # Check that all formatters are instances of logging.Formatter
        for fmt in formatter.formatters.values():
            assert isinstance(fmt, logging.Formatter)

    def test_format_debug_level(self) -> None:
        """Test formatting for DEBUG level."""
        formatter = lu.LevelSpecificFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.DEBUG,
            pathname="test_file.py",
            lineno=42,
            msg="Debug message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"

        formatted = formatter.format(record)
        expected = "DEBUG - test_function in line 42 - Debug message"
        assert formatted == expected

    def test_format_info_level(self) -> None:
        """Test formatting for INFO level."""
        formatter = lu.LevelSpecificFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Info message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        expected = "Info message"
        assert formatted == expected

    def test_format_warning_level(self) -> None:
        """Test formatting for WARNING level."""
        formatter = lu.LevelSpecificFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test_file.py",
            lineno=42,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        expected = "WARNING: Warning message"
        assert formatted == expected

    def test_format_error_level(self) -> None:
        """Test formatting for ERROR level."""
        formatter = lu.LevelSpecificFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test_file.py",
            lineno=42,
            msg="Error message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"

        formatted = formatter.format(record)
        expected = "ERROR: test_function - Error message"
        assert formatted == expected

    def test_format_critical_level(self) -> None:
        """Test formatting for CRITICAL level."""
        formatter = lu.LevelSpecificFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.CRITICAL,
            pathname="test_file.py",
            lineno=42,
            msg="Critical message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        record.filename = "test_file.py"

        formatted = formatter.format(record)
        expected = "CRITICAL: test_function in test_file.py:42 - Critical message"
        assert formatted == expected

    def test_format_unknown_level(self) -> None:
        """Test formatting for unknown level falls back to INFO format."""
        formatter = lu.LevelSpecificFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=999,  # Unknown level
            pathname="test_file.py",
            lineno=42,
            msg="Unknown level message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        expected = "Unknown level message"
        assert formatted == expected


class TestSetupLogger:
    """Test the setup_logger function."""

    def test_setup_logger_basic(self) -> None:
        """Test basic logger setup without level specification."""
        logger_name = "test_logger"
        logger = lu.setup_logger(logger_name)

        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert isinstance(logger.handlers[0].formatter, lu.LevelSpecificFormatter)

    def test_setup_logger_with_level(self) -> None:
        """Test logger setup with specific level."""
        logger_name = "test_logger_with_level"
        level = logging.DEBUG
        logger = lu.setup_logger(logger_name, level)

        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name
        assert logger.level == level
        assert len(logger.handlers) == 1

    def test_setup_logger_existing_logger(self) -> None:
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

    def test_setup_logger_different_levels(self) -> None:
        """Test that setup_logger can set different levels for same logger."""
        logger_name = "test_level_logger"

        # Setup with DEBUG level
        logger1 = lu.setup_logger(logger_name, logging.DEBUG)
        assert logger1.level == logging.DEBUG

        # Setup same logger with INFO level
        logger2 = lu.setup_logger(logger_name, logging.INFO)
        assert logger2.level == logging.INFO
        assert logger1 is logger2  # Same logger instance

    def test_setup_logger_none_level(self) -> None:
        """Test that setup_logger handles None level correctly."""
        logger_name = "test_none_level_logger"
        logger = lu.setup_logger(logger_name, None)

        assert isinstance(logger, logging.Logger)
        # When level is None, logger level should be NOTSET (0)
        assert logger.level == logging.NOTSET

    def test_setup_logger_handler_formatter(self) -> None:
        """Test that the handler has the correct formatter."""
        logger_name = "test_formatter_logger"
        logger = lu.setup_logger(logger_name)

        handler = logger.handlers[0]
        assert isinstance(handler.formatter, lu.LevelSpecificFormatter)


class TestSetGlobalLogLevel:
    """Test the set_global_log_level function."""

    def test_set_global_log_level_root_logger(self) -> None:
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

    def test_set_global_log_level_existing_loggers(self) -> None:
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

    def test_set_global_log_level_all_levels(self) -> None:
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

    def test_set_global_log_level_with_mock(self) -> None:
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


@pytest.mark.fast
def test_logging_utils_integration() -> None:
    """Integration test for logging utilities."""
    # Test the complete flow
    logger_name = "integration_test_logger"
    level = logging.DEBUG

    # Setup logger
    logger = lu.setup_logger(logger_name, level)

    # Set global level
    lu.set_global_log_level(logging.INFO)

    # Verify logger level was changed by global level setting
    assert logger.level == logging.INFO

    # Verify root logger has global level
    assert logging.getLogger().level == logging.INFO

"""Tests for the logging utilities module."""

import logging

import pytest

import src.logging_utils as lu


@pytest.mark.fast
def test_formatter_initialization() -> None:
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


@pytest.mark.fast
def test_format_debug_level() -> None:
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


@pytest.mark.fast
def test_format_info_level() -> None:
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


@pytest.mark.fast
def test_format_warning_level() -> None:
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


@pytest.mark.fast
def test_format_error_level() -> None:
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


@pytest.mark.fast
def test_format_critical_level() -> None:
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


@pytest.mark.fast
def test_format_unknown_level() -> None:
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

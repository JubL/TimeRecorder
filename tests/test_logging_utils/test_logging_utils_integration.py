"""Tests for the logging utilities module."""

import logging

import pytest

import src.logging_utils as lu


@pytest.mark.fast
@pytest.mark.integration
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

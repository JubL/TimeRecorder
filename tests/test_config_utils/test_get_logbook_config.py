"""Tests for the config_utils module."""

import pathlib

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_logbook_config() -> None:
    """Test extraction of Logbook configuration."""
    config: dict = {
        "logging": {
            "log_path": "test_logbook.txt",
        },
        "time_tracking": {
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    }

    result = cu.get_logbook_config(config)

    assert result["log_path"] == pathlib.Path.cwd() / "test_logbook.txt"
    assert result["full_format"] == "%d.%m.%Y %H:%M:%S"

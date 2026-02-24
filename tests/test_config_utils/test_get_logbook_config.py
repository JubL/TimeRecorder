"""Tests for the config_utils module."""

import pathlib

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_logbook_config(sample_config: dict) -> None:
    """Test extraction of Logbook configuration."""
    config = {
        **sample_config,
        "logging": {**sample_config["logging"], "log_path": "test_logbook.txt"},
    }

    result = cu.get_logbook_config(config)

    assert result["log_path"] == pathlib.Path.cwd() / "test_logbook.txt"
    assert result["full_format"] == sample_config["time_tracking"]["full_format"]

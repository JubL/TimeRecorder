"""Tests for the config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_processing_config() -> None:
    """Test extraction of processing configuration."""
    config: dict = {
        "data_processing": {
            "use_boot_time": True,
            "logging_enabled": True,
            "auto_squash": True,
            "add_missing_days": True,
        },
    }

    result = cu.get_processing_config(config)

    assert result["use_boot_time"] is True
    assert result["log_enabled"] is True
    assert result["auto_squash"] is True
    assert result["add_missing_days"] is True

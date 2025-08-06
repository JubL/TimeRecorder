"""Tests for the config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_validate_config_success() -> None:
    """Test successful configuration validation."""
    config: dict = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:25",
            "lunch_break_duration": 60,
        },
        "logging": {
            "log_path": "timereport_logbook.txt",
        },
        "work_schedule": {
            "standard_work_hours": 8,
        },
    }

    assert cu.validate_config(config) is True


@pytest.mark.fast
def test_validate_config_missing_section() -> None:
    """Test configuration validation with missing required section."""
    config: dict = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:25",
            "lunch_break_duration": 60,
        },
        # Missing 'logging' and 'work_schedule' sections
    }

    assert cu.validate_config(config) is False


@pytest.mark.fast
def test_validate_config_missing_field() -> None:
    """Test configuration validation with missing required field."""
    config: dict = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            # Missing 'end_time' and 'lunch_break_duration'
        },
        "logging": {
            "log_path": "timereport_logbook.txt",
        },
        "work_schedule": {
            "standard_work_hours": 8,
        },
    }

    assert cu.validate_config(config) is False

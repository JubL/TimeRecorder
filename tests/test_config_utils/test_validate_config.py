"""Tests for the config_utils module."""

import pathlib

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_validate_config_success() -> None:
    """Test successful configuration validation."""
    config: dict = {
        "data_processing": {
            "use_boot_time": True,
            "logging_enabled": True,
            "auto_squash": True,
            "add_missing_days": True,
        },
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:25",
            "lunch_break_duration": 60,
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
        "logging": {
            "log_path": "timereport_logbook.txt",
            "log_level": "INFO",
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
            "timezone": "Europe/Berlin",
        },
        "holidays": {
            "country": "DE",
            "subdivision": "HE",
        },
        "display": {
            "show_tail": 4,
        },
        "visualization": {
            "plot": True,
            "color_scheme": "ocean",
            "num_months": 13,
            "rolling_average_window_size": 10,
            "x_tick_interval": 3,
        },
        "analyzer": {
            "analyze_work_patterns": True,
            "outlier_method": "iqr",
            "outlier_threshold": 1.5,
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
            "log_level": "INFO",
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
            "timezone": "Europe/Berlin",
        },
        "holidays": {
            "country": "DE",
            "subdivision": "HE",
        },
        "data_processing": {},
        "display": {},
        "visualization": {},
        "analyzer": {},
    }

    assert cu.validate_config(config) is False


@pytest.mark.fast
def test_validate_config_actual_config_file() -> None:
    """Test that the actual config.yaml file passes validation."""
    config_path = pathlib.Path("config.yaml")
    if config_path.exists():
        config = cu.load_config(config_path)
        assert cu.validate_config(config) is True
    else:
        pytest.skip("config.yaml file not found")

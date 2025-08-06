"""Tests for the config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_time_recorder_config(relative_precision: float) -> None:
    """Test extraction of TimeRecorder configuration."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:25",
            "lunch_break_duration": 60,
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    }

    result = cu.get_time_recorder_config(config)

    assert result["date"] == "25.07.2025"
    assert result["start_time"] == "07:00"
    assert result["end_time"] == "17:25"
    assert result["lunch_break_duration"] == pytest.approx(60, rel=relative_precision)
    assert result["full_format"] == "%d.%m.%Y %H:%M:%S"


@pytest.mark.fast
def test_get_time_recorder_config_with_defaults(relative_precision: float) -> None:
    """Test TimeRecorder configuration with missing values."""
    config: dict = {"time_tracking": {}}

    result = cu.get_time_recorder_config(config)

    assert result["date"] == "01.08.2025"
    assert result["start_time"] == "07:00"
    assert result["end_time"] == "17:25"
    assert result["lunch_break_duration"] == pytest.approx(60, rel=relative_precision)

"""Tests for the config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_time_recorder_config(sample_config: dict, relative_precision: float) -> None:
    """Test extraction of TimeRecorder configuration."""
    result = cu.get_time_recorder_config(sample_config)

    assert result["date"] == sample_config["time_tracking"]["date"]
    assert result["start_time"] == sample_config["time_tracking"]["start_time"]
    assert result["end_time"] == sample_config["time_tracking"]["end_time"]
    assert result["lunch_break_duration"] == pytest.approx(
        sample_config["time_tracking"]["lunch_break_duration"],
        rel=relative_precision,
    )
    assert result["full_format"] == sample_config["time_tracking"]["full_format"]

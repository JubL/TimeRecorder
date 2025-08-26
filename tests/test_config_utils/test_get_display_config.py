"""Tests for the get_display_config function in config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_display_config_complete() -> None:
    """Test extraction of complete display configuration."""
    config = {
        "display": {
            "show_tail": 5,
            "calculate_weekly_hours": True,
            "calculate_daily_overhours": False,
        },
    }

    result = cu.get_display_config(config)

    assert result["show_tail"] == 5
    assert result["calculate_weekly_hours"] is True
    assert result["calculate_daily_overhours"] is False


@pytest.mark.fast
def test_get_display_config_missing_display_section() -> None:
    """Test extraction when display section is missing from config."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
        },
        "logging": {
            "log_path": "test.csv",
        },
    }

    result = cu.get_display_config(config)

    # All values should be None when display section is missing
    assert result["show_tail"] is None
    assert result["calculate_weekly_hours"] is None
    assert result["calculate_daily_overhours"] is None


@pytest.mark.fast
def test_get_display_config_empty_display_section() -> None:
    """Test extraction when display section exists but is empty."""
    config = {
        "display": {},
    }

    result = cu.get_display_config(config)

    # All values should be None when display section is empty
    assert result["show_tail"] is None
    assert result["calculate_weekly_hours"] is None
    assert result["calculate_daily_overhours"] is None


@pytest.mark.fast
def test_get_display_config_partial_configuration() -> None:
    """Test extraction when only some display options are provided."""
    config = {
        "display": {
            "show_tail": 10,
            # calculate_weekly_hours and calculate_daily_overhours are missing
        },
    }

    result = cu.get_display_config(config)

    assert result["show_tail"] == 10
    assert result["calculate_weekly_hours"] is None
    assert result["calculate_daily_overhours"] is None


@pytest.mark.fast
def test_get_display_config_with_other_sections() -> None:
    """Test extraction when config contains other sections alongside display."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
        },
        "display": {
            "show_tail": 3,
            "calculate_weekly_hours": True,
            "calculate_daily_overhours": True,
        },
        "logging": {
            "log_path": "test.csv",
        },
        "work_schedule": {
            "standard_work_hours": 8,
        },
    }

    result = cu.get_display_config(config)

    assert result["show_tail"] == 3
    assert result["calculate_weekly_hours"] is True
    assert result["calculate_daily_overhours"] is True


@pytest.mark.fast
def test_get_display_config_return_structure() -> None:
    """Test that the function returns the expected dictionary structure."""
    config = {
        "display": {
            "show_tail": 7,
            "calculate_weekly_hours": True,
            "calculate_daily_overhours": False,
        },
    }

    result = cu.get_display_config(config)

    # Check that result is a dictionary with exactly the expected keys
    assert isinstance(result, dict)
    assert set(result.keys()) == {"show_tail", "calculate_weekly_hours", "calculate_daily_overhours"}

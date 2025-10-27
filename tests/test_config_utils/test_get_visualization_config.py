"""Tests for the get_visualization_config function in config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_visualization_config_complete() -> None:
    """Test extraction of complete visualization configuration."""
    config = {
        "time_tracking": {
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
        "visualization": {
            "color_scheme": "ocean",
            "num_months": 12,
            "plot": True,
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
        },
    }

    result = cu.get_visualization_config(config)

    assert result["color_scheme"] == "ocean"
    assert result["num_months"] == 12
    assert result["plot"] is True
    assert result["standard_work_hours"] == 8
    assert result["work_days"] == [0, 1, 2, 3, 4]
    assert result["full_format"] == "%d.%m.%Y %H:%M:%S"


@pytest.mark.fast
def test_get_visualization_config_missing_all_sections() -> None:
    """Test extraction when all required sections are missing from config."""
    config = {
        "logging": {
            "log_path": "test.csv",
        },
        "data_processing": {
            "use_boot_time": True,
        },
    }

    result = cu.get_visualization_config(config)

    # All values should be None when sections are missing
    assert result["color_scheme"] is None
    assert result["num_months"] is None
    assert result["plot"] is None
    assert result["standard_work_hours"] is None
    assert result["work_days"] is None
    assert result["full_format"] is None


@pytest.mark.fast
def test_get_visualization_config_empty_sections() -> None:
    """Test extraction when sections exist but are empty."""
    config: dict[str, dict] = {
        "time_tracking": {},
        "visualization": {},
        "work_schedule": {},
    }

    result = cu.get_visualization_config(config)

    # All values should be None when sections are empty
    assert result["color_scheme"] is None
    assert result["num_months"] is None
    assert result["plot"] is None
    assert result["standard_work_hours"] is None
    assert result["work_days"] is None
    assert result["full_format"] is None


@pytest.mark.fast
def test_get_visualization_config_partial_configuration() -> None:
    """Test extraction when only some visualization options are provided."""
    config = {
        "time_tracking": {
            "full_format": "%Y-%m-%d %H:%M",
        },
        "visualization": {
            "color_scheme": "viridis",
            # num_months and plot are missing
        },
        "work_schedule": {
            "standard_work_hours": 7.5,
            # work_days is missing
        },
    }

    result = cu.get_visualization_config(config)

    assert result["color_scheme"] == "viridis"
    assert result["num_months"] is None
    assert result["plot"] is None
    assert result["standard_work_hours"] == 7.5
    assert result["work_days"] is None
    assert result["full_format"] == "%Y-%m-%d %H:%M"


@pytest.mark.fast
def test_get_visualization_config_different_data_types() -> None:
    """Test extraction with different data types for visualization options."""
    config = {
        "time_tracking": {
            "full_format": "%d/%m/%Y",
        },
        "visualization": {
            "color_scheme": "plasma",
            "num_months": 0,  # Zero value
            "plot": False,  # False boolean
        },
        "work_schedule": {
            "standard_work_hours": 6.0,  # Float value
            "work_days": [1, 2, 3],  # Partial week
        },
    }

    result = cu.get_visualization_config(config)

    assert result["color_scheme"] == "plasma"
    assert result["num_months"] == 0
    assert result["plot"] is False
    assert result["standard_work_hours"] == 6.0
    assert result["work_days"] == [1, 2, 3]
    assert result["full_format"] == "%d/%m/%Y"


@pytest.mark.fast
def test_get_visualization_config_with_other_sections() -> None:
    """Test extraction when config contains other sections alongside visualization."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
        "visualization": {
            "color_scheme": "magma",
            "num_months": 6,
            "rolling_average_window_size": 10,
            "plot": True,
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4, 5],
            "timezone": "Europe/Berlin",
        },
        "logging": {
            "log_path": "test.csv",
        },
        "data_processing": {
            "use_boot_time": True,
        },
    }

    result = cu.get_visualization_config(config)

    assert result["color_scheme"] == "magma"
    assert result["num_months"] == 6
    assert result["rolling_average_window_size"] == 10
    assert result["plot"] is True
    assert result["standard_work_hours"] == 8
    assert result["work_days"] == [0, 1, 2, 3, 4, 5]
    assert result["full_format"] == "%d.%m.%Y %H:%M:%S"


@pytest.mark.fast
def test_get_visualization_config_return_structure() -> None:
    """Test that the function returns the expected dictionary structure."""
    config = {
        "time_tracking": {
            "full_format": "%d.%m.%Y",
        },
        "visualization": {
            "color_scheme": "inferno",
            "num_months": 3,
            "rolling_average_window_size": 10,
            "plot": True,
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [1, 2, 3, 4, 5],
        },
    }

    result = cu.get_visualization_config(config)

    # Check that result is a dictionary with exactly the expected keys
    assert isinstance(result, dict)
    expected_keys = {
        "color_scheme",
        "num_months",
        "rolling_average_window_size",
        "plot",
        "standard_work_hours",
        "work_days",
        "full_format",
    }
    assert set(result.keys()) == expected_keys


@pytest.mark.fast
def test_get_visualization_config_missing_individual_sections() -> None:
    """Test extraction when individual sections are missing."""
    # Missing time_tracking section
    config_no_time_tracking = {
        "visualization": {
            "color_scheme": "cividis",
            "num_months": 9,
            "rolling_average_window_size": 10,
            "plot": False,
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
        },
    }

    result = cu.get_visualization_config(config_no_time_tracking)

    assert result["color_scheme"] == "cividis"
    assert result["num_months"] == 9
    assert result["rolling_average_window_size"] == 10
    assert result["plot"] is False
    assert result["standard_work_hours"] == 8
    assert result["work_days"] == [0, 1, 2, 3, 4]
    assert result["full_format"] is None

    # Missing visualization section
    config_no_visualization = {
        "time_tracking": {
            "full_format": "%Y-%m-%d",
        },
        "work_schedule": {
            "standard_work_hours": 7,
            "work_days": [1, 2, 3, 4, 5],
        },
    }

    result = cu.get_visualization_config(config_no_visualization)

    assert result["color_scheme"] is None
    assert result["num_months"] is None
    assert result["rolling_average_window_size"] is None
    assert result["plot"] is None
    assert result["standard_work_hours"] == 7
    assert result["work_days"] == [1, 2, 3, 4, 5]
    assert result["full_format"] == "%Y-%m-%d"

    # Missing work_schedule section
    config_no_work_schedule = {
        "time_tracking": {
            "full_format": "%d.%m.%Y %H:%M",
        },
        "visualization": {
            "color_scheme": "twilight",
            "num_months": 15,
            "rolling_average_window_size": 10,
            "plot": True,
        },
    }

    result = cu.get_visualization_config(config_no_work_schedule)

    assert result["color_scheme"] == "twilight"
    assert result["num_months"] == 15
    assert result["rolling_average_window_size"] == 10
    assert result["plot"] is True
    assert result["standard_work_hours"] is None
    assert result["work_days"] is None
    assert result["full_format"] == "%d.%m.%Y %H:%M"

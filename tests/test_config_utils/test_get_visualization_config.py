"""Tests for the get_visualization_config function in config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_visualization_config_complete(sample_config: dict) -> None:
    """Test extraction of complete visualization configuration."""
    config = {
        **sample_config,
        "visualization": {**sample_config["visualization"], "num_months": 12},
    }

    result = cu.get_visualization_config(config)

    assert result["color_scheme"] == sample_config["visualization"]["color_scheme"]
    assert result["num_months"] == 12
    assert result["plot"] is True
    assert result["standard_work_hours"] == sample_config["work_schedule"]["standard_work_hours"]
    assert result["work_days"] == sample_config["work_schedule"]["work_days"]
    assert result["full_format"] == sample_config["time_tracking"]["full_format"]


@pytest.mark.fast
def test_get_visualization_config_missing_all_sections(sample_config: dict) -> None:
    """Test extraction when all required sections are missing from config."""
    config = {k: v for k, v in sample_config.items() if k not in ("time_tracking", "visualization", "work_schedule")}

    result = cu.get_visualization_config(config)

    # All values should be None when sections are missing
    assert result["color_scheme"] is None
    assert result["num_months"] is None
    assert result["plot"] is None
    assert result["standard_work_hours"] is None
    assert result["x_tick_interval"] is None
    assert result["work_days"] is None
    assert result["full_format"] is None


@pytest.mark.fast
def test_get_visualization_config_empty_sections(sample_config: dict) -> None:
    """Test extraction when sections exist but are empty."""
    config = {**sample_config, "time_tracking": {}, "visualization": {}, "work_schedule": {}}

    result = cu.get_visualization_config(config)

    # All values should be None when sections are empty
    assert result["color_scheme"] is None
    assert result["num_months"] is None
    assert result["plot"] is None
    assert result["standard_work_hours"] is None
    assert result["x_tick_interval"] is None
    assert result["work_days"] is None
    assert result["full_format"] is None


@pytest.mark.fast
def test_get_visualization_config_partial_configuration(sample_config: dict) -> None:
    """Test extraction when only some visualization options are provided."""
    config = {
        **sample_config,
        "time_tracking": {"full_format": "%Y-%m-%d %H:%M"},
        "visualization": {"color_scheme": "viridis"},  # num_months and plot are missing
        "work_schedule": {"standard_work_hours": 7.5},  # work_days is missing
    }

    result = cu.get_visualization_config(config)

    assert result["color_scheme"] == "viridis"
    assert result["num_months"] is None
    assert result["plot"] is None
    assert result["standard_work_hours"] == 7.5
    assert result["x_tick_interval"] is None
    assert result["work_days"] is None
    assert result["full_format"] == "%Y-%m-%d %H:%M"


@pytest.mark.fast
def test_get_visualization_config_different_data_types(sample_config: dict) -> None:
    """Test extraction with different data types for visualization options."""
    config = {
        **sample_config,
        "time_tracking": {**sample_config["time_tracking"], "full_format": "%d/%m/%Y"},
        "visualization": {
            **sample_config["visualization"],
            "color_scheme": "plasma",
            "num_months": 0,  # Zero value
            "plot": False,  # False boolean
            "x_tick_interval": 3,
        },
        "work_schedule": {
            **sample_config["work_schedule"],
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
    assert result["x_tick_interval"] == 3


@pytest.mark.fast
def test_get_visualization_config_with_other_sections(sample_config: dict) -> None:
    """Test extraction when config contains other sections alongside visualization."""
    config = {
        **sample_config,
        "visualization": {
            **sample_config["visualization"],
            "color_scheme": "magma",
            "num_months": 6,
            "x_tick_interval": 4,
        },
        "work_schedule": {**sample_config["work_schedule"], "work_days": [0, 1, 2, 3, 4, 5]},
    }

    result = cu.get_visualization_config(config)

    assert result["color_scheme"] == "magma"
    assert result["num_months"] == 6
    assert result["rolling_average_window_size"] == 10
    assert result["plot"] is True
    assert result["standard_work_hours"] == 8
    assert result["work_days"] == [0, 1, 2, 3, 4, 5]
    assert result["full_format"] == sample_config["time_tracking"]["full_format"]
    assert result["x_tick_interval"] == 4


@pytest.mark.fast
def test_get_visualization_config_return_structure(sample_config: dict) -> None:
    """Test that the function returns the expected dictionary structure."""
    config = {
        **sample_config,
        "time_tracking": {**sample_config["time_tracking"], "full_format": "%d.%m.%Y"},
        "visualization": {
            **sample_config["visualization"],
            "color_scheme": "inferno",
            "num_months": 3,
        },
        "work_schedule": {**sample_config["work_schedule"], "work_days": [1, 2, 3, 4, 5]},
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
        "x_tick_interval",
        "histogram_bin_width",
    }
    assert set(result.keys()) == expected_keys


@pytest.mark.fast
def test_get_visualization_config_missing_individual_sections(sample_config: dict) -> None:
    """Test extraction when individual sections are missing."""
    # Missing time_tracking section
    config_no_time_tracking = {k: v for k, v in sample_config.items() if k != "time_tracking"}
    config_no_time_tracking["visualization"] = {
        **sample_config["visualization"],
        "color_scheme": "cividis",
        "num_months": 9,
        "plot": False,
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
    config_no_visualization = {k: v for k, v in sample_config.items() if k != "visualization"}
    config_no_visualization["time_tracking"] = {"full_format": "%Y-%m-%d"}
    config_no_visualization["work_schedule"] = {
        **sample_config["work_schedule"],
        "standard_work_hours": 7,
        "work_days": [1, 2, 3, 4, 5],
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
    config_no_work_schedule = {k: v for k, v in sample_config.items() if k != "work_schedule"}
    config_no_work_schedule["time_tracking"] = {"full_format": "%d.%m.%Y %H:%M"}
    config_no_work_schedule["visualization"] = {
        **sample_config["visualization"],
        "color_scheme": "twilight",
        "num_months": 15,
    }

    result = cu.get_visualization_config(config_no_work_schedule)

    assert result["color_scheme"] == "twilight"
    assert result["num_months"] == 15
    assert result["rolling_average_window_size"] == 10
    assert result["plot"] is True
    assert result["standard_work_hours"] is None
    assert result["work_days"] is None
    assert result["full_format"] == "%d.%m.%Y %H:%M"

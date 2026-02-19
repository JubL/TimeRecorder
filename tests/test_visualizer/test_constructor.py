"""Unit tests for the Visualizer constructor."""

import pandas as pd
import pytest

import src.config_utils as cu
import src.visualizer as viz


@pytest.mark.fast
def test_constructor_basic_initialization(sample_config: dict) -> None:
    """Test basic Visualizer initialization with minimal data."""
    # Create sample DataFrame
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [8.0, 7.5],
            "overtime": [0.0, 0.5],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    assert visualizer.df is not None
    assert visualizer.full_format == "%d.%m.%Y %H:%M:%S"
    assert visualizer.date_format == "%d.%m.%Y"
    assert visualizer.time_format == "%H:%M:%S"
    assert visualizer.num_months == 12
    assert visualizer.rolling_average_window_size == 10
    assert visualizer.standard_work_hours == 8.0
    assert visualizer.work_days == [0, 1, 2, 3, 4]
    assert len(visualizer.work_colors) == 6


@pytest.mark.fast
def test_constructor_all_color_schemes(sample_config: dict) -> None:
    """Test Visualizer initialization with all available color schemes."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    color_schemes = ["ocean", "forest", "sunset", "lavender", "coral"]

    for scheme in color_schemes:
        visualization_config = cu.get_visualization_config(sample_config)
        visualization_config["color_scheme"] = scheme
        visualization_config["num_months"] = 6

        visualizer = viz.Visualizer(df, visualization_config)
        assert visualizer.work_colors == viz.COLOR_SCHEMES_WORK[scheme]


@pytest.mark.fast
def test_constructor_data_filtering(sample_config: dict) -> None:
    """Test that constructor filters data to last num_months."""
    # Create DataFrame with dates spanning multiple months
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    df = pd.DataFrame(
        {
            "date": [d.strftime("%d.%m.%Y") for d in dates],
            "start_time": ["08:00:00"] * len(dates),
            "work_time": [8.0] * len(dates),
            "overtime": [0.0] * len(dates),
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 3

    visualizer = viz.Visualizer(df, visualization_config)

    # Should filter to last 3 months
    expected_start_date = pd.Timestamp("2024-10-01")
    assert visualizer.df["date"].min() >= expected_start_date


@pytest.mark.fast
def test_constructor_format_parsing(sample_config: dict) -> None:
    """Test constructor correctly parses different format strings."""
    df = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["full_format"] = "%Y-%m-%d %H:%M:%S"
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    assert visualizer.date_format == "%Y-%m-%d"
    assert visualizer.time_format == "%H:%M:%S"


@pytest.mark.fast
def test_constructor_work_days_custom(sample_config: dict) -> None:
    """Test constructor with custom work days."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    custom_work_days = [1, 2, 3, 4, 5]  # Tuesday to Saturday

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualization_config["work_days"] = custom_work_days

    visualizer = viz.Visualizer(df, visualization_config)

    assert visualizer.work_days == custom_work_days


@pytest.mark.fast
def test_constructor_empty_dataframe(sample_config: dict) -> None:
    """Test constructor with empty DataFrame."""
    df = pd.DataFrame(columns=["date", "work_time", "overtime"])

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    assert visualizer.df.empty
    assert len(visualizer.work_colors) == 6


@pytest.mark.fast
def test_constructor_standard_work_hours_float(sample_config: dict) -> None:
    """Test constructor with float standard work hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualization_config["standard_work_hours"] = 7.5

    visualizer = viz.Visualizer(df, visualization_config)

    assert visualizer.standard_work_hours == 7.5

"""Unit tests for the Visualizer constructor."""

import pandas as pd
import pytest

import src.visualizer as viz


@pytest.mark.fast
def test_constructor_basic_initialization() -> None:
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

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    assert visualizer.df is not None
    assert visualizer.full_format == "%d.%m.%Y %H:%M:%S"
    assert visualizer.date_format == "%d.%m.%Y"
    assert visualizer.time_format == "%H:%M:%S"
    assert visualizer.num_months == 12
    assert visualizer.standard_work_hours == 8.0
    assert visualizer.work_days == [0, 1, 2, 3, 4]
    assert len(visualizer.work_colors) == 6


@pytest.mark.fast
def test_constructor_all_color_schemes() -> None:
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
        data = {
            "full_format": "%d.%m.%Y %H:%M:%S",
            "color_scheme": scheme,
            "num_months": 6,
            "standard_work_hours": 8.0,
            "work_days": [0, 1, 2, 3, 4],
        }

        visualizer = viz.Visualizer(df, data)
        assert visualizer.work_colors == viz.COLOR_SCHEMES_WORK[scheme]


@pytest.mark.fast
def test_constructor_data_filtering() -> None:
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

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 3,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    # Should filter to last 3 months
    expected_start_date = pd.Timestamp("2024-10-01")
    assert visualizer.df["date"].min() >= expected_start_date


@pytest.mark.fast
def test_constructor_format_parsing() -> None:
    """Test constructor correctly parses different format strings."""
    df = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    data = {
        "full_format": "%Y-%m-%d %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    assert visualizer.date_format == "%Y-%m-%d"
    assert visualizer.time_format == "%H:%M:%S"


@pytest.mark.fast
def test_constructor_work_days_custom() -> None:
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

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": custom_work_days,
    }

    visualizer = viz.Visualizer(df, data)

    assert visualizer.work_days == custom_work_days


@pytest.mark.fast
def test_constructor_empty_dataframe() -> None:
    """Test constructor with empty DataFrame."""
    df = pd.DataFrame(columns=["date", "work_time", "overtime"])

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    assert visualizer.df.empty
    assert len(visualizer.work_colors) == 6


@pytest.mark.fast
def test_constructor_standard_work_hours_float() -> None:
    """Test constructor with float standard work hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 7.5,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    assert visualizer.standard_work_hours == 7.5

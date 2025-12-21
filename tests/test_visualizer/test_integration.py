"""Integration tests for the Visualizer class."""

import pandas as pd
import pytest

import src.visualizer as viz


@pytest.mark.fast
def test_visualizer_integration_complete_workflow() -> None:
    """Test complete visualizer workflow with realistic data."""
    # Create realistic work data for a month
    dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="D")
    work_data = []

    for date in dates:
        # Skip weekends (5=Saturday, 6=Sunday)
        if date.weekday() < 5:
            # Simulate realistic work patterns
            base_hours = 8.0
            overtime = 0.0

            # Add some variation
            if date.weekday() == 0:  # Monday - often longer
                base_hours = 8.5
                overtime = 0.5
            elif date.weekday() == 4:  # Friday - often shorter
                base_hours = 7.5
                overtime = 0.0

            work_data.append(
                {
                    "date": date.strftime("%d.%m.%Y"),
                    "start_time": "08:00:00",
                    "work_time": base_hours,
                    "overtime": overtime,
                },
            )

    df = pd.DataFrame(work_data)

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)

    # Test that data was processed correctly
    assert len(visualizer.df) > 0
    assert pd.api.types.is_datetime64_any_dtype(visualizer.df["date"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # Test that work_time adjustment works correctly
    visualizer.plot_daily_work_hours()

    # Check that Monday's work_time was adjusted (8.5 + 0.5 = 9.0, should become 8.0)
    monday_data = visualizer.df[visualizer.df["date"].dt.weekday == 0]
    if not monday_data.empty:
        assert monday_data["work_time"].iloc[0] == 8.0


@pytest.mark.fast
def test_visualizer_integration_multiple_months() -> None:
    """Test visualizer with data spanning multiple months."""
    # Create data for 3 months
    dates = pd.date_range(start="2024-01-01", end="2024-03-31", freq="D")
    work_data = []

    work_data = [
        {
            "date": date.strftime("%d.%m.%Y"),
            "start_time": "08:00:00",
            "work_time": 8.0,
            "overtime": 0.0,
        }
        for date in dates
        if date.weekday() < 5  # Weekdays only
    ]

    df = pd.DataFrame(work_data)

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "forest",
        "num_months": 2,  # Only show last 2 months
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)

    # Should filter to last 2 months
    assert len(visualizer.df) < len(df)
    assert visualizer.df["date"].min() < pd.Timestamp("2024-02-01")


@pytest.mark.fast
def test_visualizer_integration_all_color_schemes() -> None:
    """Test visualizer with all available color schemes."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00"],
            "work_time": [8.0, 8.5, 7.5],
            "overtime": [0.0, 0.5, 0.0],
        },
    )

    color_schemes = ["ocean", "forest", "sunset", "lavender", "coral"]

    for scheme in color_schemes:  # TODO: use parametrize fixture instead
        data = {
            "full_format": "%d.%m.%Y %H:%M:%S",
            "color_scheme": scheme,
            "num_months": 12,
            "rolling_average_window_size": 10,
            "x_tick_interval": 3,
            "standard_work_hours": 8.0,
            "work_days": [0, 1, 2, 3, 4],
        }

        visualizer = viz.Visualizer(df, data)

        # Test that each color scheme works correctly
        assert visualizer.work_colors == viz.COLOR_SCHEMES_WORK[scheme]

        # Test plotting with each scheme
        visualizer.plot_daily_work_hours()

        # Verify work_time adjustment
        assert visualizer.df["work_time"].iloc[1] == 8.0  # 8.5 - 0.5


@pytest.mark.fast
def test_visualizer_integration_different_formats() -> None:
    """Test visualizer with different date formats."""
    test_cases = [  # TODO: use parametrize fixture instead
        ("%d.%m.%Y", "01.01.2024"),
        ("%Y-%m-%d", "2024-01-01"),
        ("%m/%d/%Y", "01/01/2024"),
    ]

    for date_format, date_str in test_cases:
        full_format = f"{date_format} %H:%M:%S"
        df = pd.DataFrame(
            {
                "date": [date_str],
                "start_time": ["08:00:00"],
                "work_time": [8.0],
                "overtime": [0.0],
            },
        )

        data = {
            "full_format": full_format,
            "color_scheme": "ocean",
            "num_months": 12,
            "rolling_average_window_size": 10,
            "standard_work_hours": 8.0,
            "work_days": [0, 1, 2, 3, 4],
            "x_tick_interval": 3,
        }

        visualizer = viz.Visualizer(df, data)

        # Test that date parsing works correctly
        assert pd.api.types.is_datetime64_any_dtype(visualizer.df["date"])
        assert not visualizer.df["date"].isna().any()

        # Test plotting
        visualizer.plot_daily_work_hours()


@pytest.mark.fast
def test_visualizer_integration_edge_cases() -> None:
    """Test visualizer with various edge cases."""
    # Test with very large overtime
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["07:00:00", "07:00:00"],
            "work_time": [12.0, 16.0],
            "overtime": [4.0, 8.0],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)
    visualizer.plot_daily_work_hours()

    # Work time should be adjusted to standard hours
    assert visualizer.df["work_time"].iloc[0] == 8.0  # 12.0 - 4.0
    assert visualizer.df["work_time"].iloc[1] == 8.0  # 16.0 - 8.0


@pytest.mark.fast
def test_visualizer_integration_custom_work_days() -> None:
    """Test visualizer with custom work days."""
    # Create data for a week
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "05.01.2024", "06.01.2024", "07.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00", "08:00:00", "08:00:00", "08:00:00", "08:00:00"],
            "work_time": [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0],
            "overtime": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        },
    )

    # Test with Tuesday-Saturday work schedule
    custom_work_days = [1, 2, 3, 4, 5]

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "sunset",
        "num_months": 12,
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": custom_work_days,
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)

    assert visualizer.work_days == custom_work_days
    visualizer.plot_daily_work_hours()


@pytest.mark.fast
def test_visualizer_integration_mixed_data_quality() -> None:
    """Test visualizer with mixed data quality (missing values, invalid data)."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00", "08:00:00"],
            "work_time": ["8.0", "", "invalid", "7.5"],
            "overtime": ["0.0", "1.0", "", "0.5"],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "lavender",
        "num_months": 12,
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)

    # Should handle all data quality issues gracefully
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # Missing/invalid values should be filled with 0.0
    assert visualizer.df["work_time"].iloc[1] == 0.0  # Empty string
    assert visualizer.df["work_time"].iloc[2] == 0.0  # Invalid string
    assert visualizer.df["overtime"].iloc[2] == 0.0  # Empty string

    visualizer.plot_daily_work_hours()


@pytest.mark.fast
def test_visualizer_integration_standard_work_hours_variations() -> None:
    """Test visualizer with different standard work hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [7.5, 8.5],
            "overtime": [0.0, 0.5],
        },
    )

    # Test with 7.5 hour work day
    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "coral",
        "num_months": 12,
        "rolling_average_window_size": 10,
        "standard_work_hours": 7.5,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)
    visualizer.plot_daily_work_hours()

    # Day 1: 7.5 + 0.0 = 7.5 (no adjustment)
    # Day 2: 8.5 + 0.5 = 9.0 (adjust to 7.5)
    assert visualizer.df["work_time"].iloc[0] == 7.5
    assert visualizer.df["work_time"].iloc[1] == 8.0  # 8.5 - 0.5

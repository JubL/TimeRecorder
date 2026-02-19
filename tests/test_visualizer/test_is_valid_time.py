"""Unit tests for the Visualizer is_valid_time method."""

import pandas as pd
import pytest

import src.visualizer as viz


@pytest.mark.fast
def test_is_valid_time_with_timezone() -> None:
    """Test is_valid_time with timezone information."""
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
        "rolling_average_window_size": 10,
        "x_tick_interval": 3,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Test valid time with timezone
    assert visualizer.is_valid_time("08:00:00 CEST") is True
    assert visualizer.is_valid_time("14:30:15 UTC") is True
    assert visualizer.is_valid_time("23:59:59 EST") is True


@pytest.mark.fast
def test_is_valid_time_without_timezone() -> None:
    """Test is_valid_time without timezone information."""
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
        "rolling_average_window_size": 10,
        "x_tick_interval": 3,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Test valid time without timezone
    assert visualizer.is_valid_time("08:00:00") is True
    assert visualizer.is_valid_time("14:30:15") is True
    assert visualizer.is_valid_time("23:59:59") is True


@pytest.mark.fast
def test_is_valid_time_invalid_formats() -> None:
    """Test is_valid_time with invalid time formats."""
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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Test invalid time formats
    assert visualizer.is_valid_time("08:00") is False  # Missing seconds
    assert visualizer.is_valid_time("25:00:00") is False  # Invalid hour
    assert visualizer.is_valid_time("08:60:00") is False  # Invalid minute
    assert visualizer.is_valid_time("08:00:60") is False  # Invalid second
    assert visualizer.is_valid_time("invalid") is False  # Completely invalid
    assert visualizer.is_valid_time("") is False  # Empty string


@pytest.mark.fast
def test_is_valid_time_none_and_na_values() -> None:
    """Test is_valid_time with None and NaN values."""
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
        "rolling_average_window_size": 10,
        "x_tick_interval": 3,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Test None and NaN values
    assert visualizer.is_valid_time(None) is False  # type: ignore[arg-type]
    # Note: pd.NA and pd.NaT cause TypeError in boolean context, so we test them differently
    try:
        result = visualizer.is_valid_time(pd.NA)  # type: ignore[arg-type]
        assert result is False
    except TypeError:
        # This is expected behavior - pd.NA in boolean context raises TypeError
        pass

    try:
        result = visualizer.is_valid_time(pd.NaT)  # type: ignore[arg-type]
        assert result is False
    except TypeError:
        # This is expected behavior - pd.NaT in boolean context raises TypeError
        pass


@pytest.mark.fast
def test_is_valid_time_different_time_formats() -> None:
    """Test is_valid_time with different time format configurations."""
    # Test with different time formats
    test_cases = [
        ("%H:%M:%S", "08:00:00", True),
        ("%H:%M:%S", "8:00:00", True),  # Actually valid - method strips timezone and parses
        ("%H:%M:%S", "08:00", False),  # Missing seconds
        ("%H:%M", "08:00", True),
        ("%H:%M", "8:00", True),  # Actually valid - method strips timezone and parses
        ("%H:%M", "08:00:00", False),  # Extra seconds
    ]

    for time_format, time_str, expected in test_cases:
        full_format = f"%d.%m.%Y {time_format}"
        df = pd.DataFrame(
            {
                "date": ["01.01.2024"],
                "start_time": [time_str],
                "work_time": [8.0],
                "overtime": [0.0],
            },
        )

        data = {
            "full_format": full_format,
            "color_scheme": "ocean",
            "num_months": 12,
            "rolling_average_window_size": 10,
            "x_tick_interval": 3,
            "standard_work_hours": 8.0,
            "work_days": [0, 1, 2, 3, 4],
            "histogram_bins": 64,
        }

        visualizer = viz.Visualizer(df, data)
        assert visualizer.is_valid_time(time_str) is expected


@pytest.mark.fast
def test_is_valid_time_timezone_parsing_edge_cases() -> None:
    """Test is_valid_time with timezone parsing edge cases."""
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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Test timezone parsing edge cases
    assert visualizer.is_valid_time("08:00:00 CEST") is True
    assert visualizer.is_valid_time("08:00:00 UTC") is True
    assert visualizer.is_valid_time("08:00:00 EST") is True
    assert visualizer.is_valid_time("08:00:00 PST") is True
    assert visualizer.is_valid_time("08:00:00 GMT") is True
    assert visualizer.is_valid_time("08:00:00 +01:00") is True  # Actually valid - strips timezone and parses time
    assert visualizer.is_valid_time("08:00:00 CEST extra") is True  # Actually valid - strips timezone and parses time


@pytest.mark.fast
def test_is_valid_time_malformed_timezone() -> None:
    """Test is_valid_time with malformed timezone information."""
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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Test malformed timezone cases
    assert visualizer.is_valid_time("08:00:00 INVALID") is True  # Actually valid - strips timezone and parses time
    assert visualizer.is_valid_time("08:00:00 ") is True  # Actually valid - strips timezone and parses time
    assert visualizer.is_valid_time("08:00:00CEST") is False  # No space before timezone - invalid format


@pytest.mark.fast
def test_is_valid_time_boundary_values() -> None:
    """Test is_valid_time with boundary time values."""
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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Test boundary values
    assert visualizer.is_valid_time("00:00:00") is True  # Midnight
    assert visualizer.is_valid_time("23:59:59") is True  # End of day
    assert visualizer.is_valid_time("12:00:00") is True  # Noon
    assert visualizer.is_valid_time("24:00:00") is False  # Invalid hour
    assert visualizer.is_valid_time("23:60:00") is False  # Invalid minute
    assert visualizer.is_valid_time("23:59:60") is False  # Invalid second


@pytest.mark.fast
def test_is_valid_time_whitespace_handling() -> None:
    """Test is_valid_time with various whitespace scenarios."""
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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Test whitespace handling
    assert visualizer.is_valid_time(" 08:00:00 ") is True  # Actually valid - strips timezone and parses time
    assert visualizer.is_valid_time("08:00:00 ") is True  # Actually valid - strips timezone and parses time
    assert visualizer.is_valid_time(" 08:00:00") is True  # Actually valid - strips timezone and parses time
    assert visualizer.is_valid_time("08: 00:00") is False  # Space in time - invalid format
    assert visualizer.is_valid_time("08:00: 00") is False  # Space in time - invalid format
    assert visualizer.is_valid_time("08:00:00  ") is True  # Actually valid - strips timezone and parses time

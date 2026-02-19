"""Unit tests for data filtering in the Visualizer constructor."""

import pandas as pd
import pytest

import src.visualizer as viz


@pytest.mark.fast
def test_constructor_data_filtering_exact_months() -> None:
    """Test data filtering with exact month boundaries."""
    # Create data for exactly 3 months
    dates = pd.date_range(start="2024-01-01", end="2024-03-31", freq="D")
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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Should include all data since it's exactly 3 months
    assert len(visualizer.df) == len(df)


@pytest.mark.fast
def test_constructor_data_filtering_more_than_num_months() -> None:
    """Test data filtering when data spans more than num_months."""
    # Create data for 6 months
    dates = pd.date_range(start="2024-01-01", end="2024-06-30", freq="D")
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
        "num_months": 3,  # Only last 3 months
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Should filter to last 3 months (April, May, June)
    # The filtering logic is: df["date"] > max_date - 3 months
    # max_date is 2024-06-30, so cutoff is 2024-03-31
    # So we get dates > 2024-03-31, which includes April, May, June
    expected_start_date = pd.Timestamp("2024-03-31")
    assert visualizer.df["date"].min() >= expected_start_date
    assert len(visualizer.df) < len(df)


@pytest.mark.fast
def test_constructor_data_filtering_less_than_num_months() -> None:
    """Test data filtering when data spans less than num_months."""
    # Create data for 1 month
    dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="D")
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
        "num_months": 3,  # Request 3 months but only have 1
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Should include all available data
    assert len(visualizer.df) == len(df)


@pytest.mark.fast
def test_constructor_data_filtering_zero_months() -> None:
    """Test data filtering with zero num_months."""
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
        "num_months": 0,  # Zero months
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # When num_months is 0, the filtering results in empty DataFrame
    # because max_date - 0 months = max_date, so no dates are > max_date
    assert len(visualizer.df) == 0


@pytest.mark.fast
def test_constructor_data_filtering_negative_months() -> None:
    """Test data filtering with negative num_months."""
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
        "num_months": -1,  # Negative months
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # When num_months is negative, the filtering results in empty DataFrame
    # because max_date - (-1) months = max_date + 1 month, so no dates are > max_date + 1 month
    assert len(visualizer.df) == 0


@pytest.mark.fast
def test_constructor_data_filtering_single_day() -> None:
    """Test data filtering with single day of data."""
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

    # Should include the single day
    assert len(visualizer.df) == 1


@pytest.mark.fast
def test_constructor_data_filtering_irregular_dates() -> None:
    """Test data filtering with irregular date spacing."""
    # Create data with irregular spacing (not daily)
    dates = [
        "01.01.2024",
        "05.01.2024",
        "10.01.2024",
        "15.01.2024",
        "01.02.2024",
        "05.02.2024",
        "10.02.2024",
        "15.02.2024",
        "01.03.2024",
        "05.03.2024",
        "10.03.2024",
        "15.03.2024",
    ]

    df = pd.DataFrame(
        {
            "date": dates,
            "start_time": ["08:00:00"] * len(dates),
            "work_time": [8.0] * len(dates),
            "overtime": [0.0] * len(dates),
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 2,  # Last 2 months
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Should filter to last 2 months (February and March)
    assert len(visualizer.df) < len(df)
    assert visualizer.df["date"].min() >= pd.Timestamp("2024-02-01")


@pytest.mark.fast
def test_constructor_data_filtering_leap_year() -> None:
    """Test data filtering with leap year data."""
    # Create data for leap year February
    dates = pd.date_range(start="2024-02-01", end="2024-02-29", freq="D")
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
        "num_months": 1,  # Last 1 month
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Should include all leap year February data
    assert len(visualizer.df) == 29  # 29 days in leap year February


@pytest.mark.fast
def test_constructor_data_filtering_year_boundary() -> None:
    """Test data filtering across year boundary."""
    # Create data spanning year boundary
    dates = pd.date_range(start="2023-12-01", end="2024-02-29", freq="D")
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
        "num_months": 2,  # Last 2 months
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Should filter to last 2 months (January and February 2024)
    # The filtering logic is: df["date"] > max_date - 2 months
    # max_date is 2024-02-29, so cutoff is 2023-12-29
    # So we get dates > 2023-12-29, which includes January and February 2024
    assert visualizer.df["date"].min() > pd.Timestamp("2023-12-29")
    assert visualizer.df["date"].max() <= pd.Timestamp("2024-02-29")


@pytest.mark.fast
def test_constructor_data_filtering_very_large_num_months() -> None:
    """Test data filtering with very large num_months."""
    # Create data for 1 year
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
        "num_months": 1000,  # Very large number
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    visualizer = viz.Visualizer(df, data)

    # Should include all data when num_months is very large
    assert len(visualizer.df) == len(df)


@pytest.mark.fast
def test_constructor_data_filtering_float_num_months() -> None:
    """Test data filtering with float num_months raises ValueError."""
    # Create data for 3 months
    dates = pd.date_range(start="2024-01-01", end="2024-03-31", freq="D")
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
        "num_months": 2.5,  # Float months
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
        "histogram_bins": 64,
    }

    with pytest.raises(ValueError, match="Non-integer years and months are ambiguous"):
        viz.Visualizer(df, data)

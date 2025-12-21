"""Comprehensive unit tests for the Visualizer plot_daily_work_hours method with mocking."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

import src.visualizer as viz


@pytest.mark.fast
@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_matplotlib_calls(mock_subplots: Mock, mock_show: Mock) -> None:
    """Test that plot_daily_work_hours makes correct matplotlib calls."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_tick2 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1, mock_tick2]

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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)
    visualizer.plot_daily_work_hours()

    # Verify matplotlib calls
    mock_subplots.assert_called_once_with(figsize=(8, 5))
    mock_show.assert_called_once()


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_axis_configuration(mock_subplots: Mock) -> None:
    """Test that plot_daily_work_hours configures the axis correctly."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_tick2 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1, mock_tick2]

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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)
    visualizer.plot_daily_work_hours()

    # Verify axis configuration
    mock_ax.xaxis.set_major_locator.assert_called_once()
    mock_ax.xaxis.set_major_formatter.assert_called_once()
    mock_ax.tick_params.assert_called_once_with(axis="x", which="both", length=0)
    mock_ax.set_xlabel.assert_called_once_with("Calendar Week")
    mock_ax.set_ylabel.assert_called_once_with("Work Hours")
    mock_ax.set_title.assert_called_once_with("Daily Work Hours")


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_bar_calls(mock_subplots: Mock) -> None:
    """Test that plot_daily_work_hours makes correct bar calls."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_tick2 = Mock()
    mock_tick3 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1, mock_tick2, mock_tick3]

    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00"],
            "work_time": [8.0, 7.5, 8.5],
            "overtime": [0.0, 0.5, 0.5],
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

    # Verify bar calls - should be called for each work day
    assert mock_ax.bar.call_count >= 3  # At least 3 calls (work, overtime, free days)


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_work_time_adjustment_logic(mock_subplots: Mock) -> None:
    """Test the work_time adjustment logic in plot_daily_work_hours."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_tick2 = Mock()
    mock_tick3 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1, mock_tick2, mock_tick3]

    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00"],
            "work_time": [7.0, 8.0, 10.0],  # 7.0 <= 8.0, 8.0 <= 8.0, 10.0 > 8.0
            "overtime": [0.0, 0.0, 2.0],  # 0.0, 0.0, 2.0
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

    # Before adjustment
    assert visualizer.df["work_time"].iloc[0] == 7.0
    assert visualizer.df["work_time"].iloc[1] == 8.0
    assert visualizer.df["work_time"].iloc[2] == 10.0

    visualizer.plot_daily_work_hours()

    # After adjustment
    assert visualizer.df["work_time"].iloc[0] == 7.0  # 7.0 <= 8.0, no change
    assert visualizer.df["work_time"].iloc[1] == 8.0  # 8.0 <= 8.0, no change
    assert visualizer.df["work_time"].iloc[2] == 8.0  # 10.0 > 8.0, becomes 10.0 - 2.0 = 8.0


@pytest.mark.fast
@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_empty_dataframe(mock_subplots: Mock, mock_show: Mock) -> None:
    """Test plot_daily_work_hours with empty DataFrame."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_ax.xaxis.get_ticklabels.return_value = []

    df = pd.DataFrame(columns=["date", "work_time", "overtime"])

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

    # Should still make matplotlib calls even with empty data
    mock_subplots.assert_called_once()
    mock_show.assert_called_once()


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_single_work_day(mock_subplots: Mock) -> None:
    """Test plot_daily_work_hours with only one work day."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1]

    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],  # Monday
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
        "work_days": [0],  # Only Monday
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)
    visualizer.plot_daily_work_hours()

    # Should make bar calls for the single work day
    assert mock_ax.bar.call_count >= 1


@pytest.mark.fast
@patch("matplotlib.pyplot.show")
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_no_work_days(mock_subplots: Mock, mock_show: Mock) -> None:
    """Test plot_daily_work_hours with no work days."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_tick2 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1, mock_tick2]

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
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [],  # No work days
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)
    visualizer.plot_daily_work_hours()

    # Should still make matplotlib calls but no bar calls
    mock_subplots.assert_called_once()
    mock_show.assert_called_once()
    assert mock_ax.bar.call_count == 0


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_all_negative_work_time(mock_subplots: Mock) -> None:
    """Test plot_daily_work_hours with all negative work_time (free days)."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_tick2 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1, mock_tick2]

    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["invalid", "invalid"],  # Invalid times
            "work_time": [8.0, 7.5],  # Will be set to -8.0 due to invalid times
            "overtime": [0.0, 0.0],
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

    # Should make bar calls for free days (negative work_time)
    assert mock_ax.bar.call_count >= 2  # At least 2 calls for free days


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_zero_work_time(mock_subplots: Mock) -> None:
    """Test plot_daily_work_hours with zero work_time values."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_tick2 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1, mock_tick2]

    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [0.0, 0.0],  # Zero work time
            "overtime": [0.0, 0.0],
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

    # Should make bar calls even for zero work_time because the plotting logic
    # still processes all work days, even if they have zero work time
    assert mock_ax.bar.call_count > 0


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_plot_daily_work_hours_color_scheme_usage(mock_subplots: Mock) -> None:
    """Test that plot_daily_work_hours uses the correct color scheme."""
    # Setup mock
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Mock tick labels to be iterable
    mock_tick1 = Mock()
    mock_tick2 = Mock()
    mock_ax.xaxis.get_ticklabels.return_value = [mock_tick1, mock_tick2]

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
        "color_scheme": "forest",  # Use forest color scheme
        "num_months": 12,
        "rolling_average_window_size": 10,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
        "x_tick_interval": 3,
    }

    visualizer = viz.Visualizer(df, data)
    visualizer.plot_daily_work_hours()

    # Verify that forest colors are used
    forest_colors = viz.COLOR_SCHEMES_WORK["forest"]
    assert visualizer.work_colors == forest_colors

    # Check that bar calls use the correct colors
    bar_calls = mock_ax.bar.call_args_list
    for call in bar_calls:
        call_kwargs = call[1] if len(call) > 1 else {}
        if "color" in call_kwargs:
            assert call_kwargs["color"] in forest_colors

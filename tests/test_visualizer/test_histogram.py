"""Unit tests for the Visualizer create_histogram method."""

import logging
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

import src.config_utils as cu
import src.visualizer as viz


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_create_histogram_with_positive_work_hours(
    mock_subplots: Mock,
    sample_config: dict,
) -> None:
    """Test create_histogram creates histogram when work_hours has data."""
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00"],
            "work_time": [8.0, 7.5, 9.0],
            "overtime": [0.0, 0.5, 1.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualization_config["histogram_bin_width"] = 30  # 30 minutes

    visualizer = viz.Visualizer(df, visualization_config)
    visualizer.create_work_hours_histogram()

    mock_subplots.assert_called_once_with(figsize=(8, 5))
    mock_ax.hist.assert_called_once()
    call_args = mock_ax.hist.call_args
    assert len(call_args[0][0]) == 3  # work_hours for 3 days
    bins = call_args[1]["bins"]
    assert isinstance(bins, list)
    bin_width_hours = 30 / 60  # 0.5 hours
    assert np.allclose(np.diff(bins), bin_width_hours)
    assert call_args[1]["color"] == visualizer.work_colors[0]
    assert call_args[1]["edgecolor"] == "white"
    mock_ax.set_xlabel.assert_called_once_with("Work Hours")
    mock_ax.set_ylabel.assert_called_once_with("Frequency")
    mock_ax.set_title.assert_called_once_with("Distribution of Daily Work Hours")


@pytest.mark.fast
def test_create_histogram_empty_work_hours_returns_early(
    sample_config: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test create_histogram logs warning and returns when no positive work hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [0.0, 0.0],
            "overtime": [0.0, 0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    with caplog.at_level(logging.WARNING, logger="src.visualizer"):
        visualizer.create_work_hours_histogram()

    assert "No work days with positive hours to display in histogram" in caplog.text


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_create_histogram_empty_work_hours_no_subplots(
    mock_subplots: Mock,
    sample_config: dict,
) -> None:
    """Test create_histogram does not create subplots when work_hours is empty."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [0.0, 0.0],
            "overtime": [0.0, 0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)
    visualizer.create_work_hours_histogram()

    mock_subplots.assert_not_called()


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_create_histogram_uses_histogram_bin_width(
    mock_subplots: Mock,
    sample_config: dict,
) -> None:
    """Test create_histogram uses histogram_bin_width from config."""
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

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
    visualization_config["histogram_bin_width"] = 15  # 15 minutes

    visualizer = viz.Visualizer(df, visualization_config)
    visualizer.create_work_hours_histogram()

    bins = mock_ax.hist.call_args[1]["bins"]
    expected_bin_width = 15 / 60  # 0.25 hours
    assert np.allclose(np.diff(bins), expected_bin_width)


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_create_work_hours_per_weekday_histogram(
    mock_subplots: Mock,
    sample_config: dict,
) -> None:
    """Test create_work_hours_per_weekday_histogram."""
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # 01.01.2024=Mon, 02.01.2024=Tue, 03.01.2024=Wed, 04.01.2024=Thu, 05.01.2024=Fri
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "05.01.2024"],
            "start_time": ["08:00:00"] * 5,
            "work_time": [8.0, 8.0, 8.0, 8.0, 8.0],
            "overtime": [0.0] * 5,
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)
    visualizer.create_work_hours_per_weekday_histogram()

    mock_subplots.assert_called_once_with(figsize=(8, 5))
    mock_ax.bar.assert_called_once()
    call_args = mock_ax.bar.call_args
    labels, values = call_args[0][0], call_args[0][1]
    assert labels == ["Mon", "Tue", "Wed", "Thu", "Fri"]
    # 5 days * 8h = 40h total, normalized to 8*5=40, so each day should be 8.0
    assert np.allclose(values, [8.0, 8.0, 8.0, 8.0, 8.0])
    mock_ax.set_xlabel.assert_called_once_with("Weekday")
    mock_ax.set_ylabel.assert_called_once_with("Work Hours")
    assert "Work Hours per Weekday" in mock_ax.set_title.call_args[0][0]


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
def test_create_work_hours_per_weekday_histogram_uneven_distribution(
    mock_subplots: Mock,
    sample_config: dict,
) -> None:
    """Test normalization uses avg hours per occurrence (divide by count per weekday)."""
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # 01.01=Mon(12h), 02.01=Tue(8h), 03.01=Wed(8h), 04.01=Thu(8h), 08.01=Mon(4h)
    # Mon: avg (12+4)/2=8, Tue: 8, Wed: 8, Thu: 8, Fri: 0.
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "08.01.2024"],
            "start_time": ["08:00:00"] * 5,
            "work_time": [12.0, 8.0, 8.0, 8.0, 4.0],
            "overtime": [0.0] * 5,
        },
    )
    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)
    visualizer.create_work_hours_per_weekday_histogram()

    values = mock_ax.bar.call_args[0][1]
    assert np.allclose(values, [8.0, 8.0, 8.0, 8.0, 0.0])


@pytest.mark.fast
def test_create_work_hours_per_weekday_histogram_empty_returns_early(
    sample_config: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test create_work_hours_per_weekday_histogram logs warning when no positive work hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [0.0, 0.0],
            "overtime": [0.0, 0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualizer = viz.Visualizer(df, visualization_config)

    with caplog.at_level(logging.WARNING, logger="src.visualizer"):
        visualizer.create_work_hours_per_weekday_histogram()

    assert "No work days with positive hours" in caplog.text

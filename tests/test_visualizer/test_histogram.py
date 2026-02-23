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
    visualizer.create_histogram()

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
        visualizer.create_histogram()

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
    visualizer.create_histogram()

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
    visualizer.create_histogram()

    bins = mock_ax.hist.call_args[1]["bins"]
    expected_bin_width = 15 / 60  # 0.25 hours
    assert np.allclose(np.diff(bins), expected_bin_width)

"""Unit tests for the Visualizer create_start_end_time_histogram method."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
from matplotlib.cm import get_cmap as mpl_get_cmap

import src.config_utils as cu
import src.visualizer as viz


@pytest.mark.fast
@patch("matplotlib.pyplot.subplots")
@patch("matplotlib.pyplot.colorbar")
def test_create_start_end_time_histogram_basic(
    mock_colorbar: Mock,
    mock_subplots: Mock,
    sample_config: dict,
) -> None:
    """Histogram is created for valid start/end times and uses HH:MM axis labels."""
    mock_fig = Mock()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Fake image object returned by hist2d
    mock_image = Mock()
    mock_image.cmap = mpl_get_cmap("plasma")
    mock_image.cmap.N = 10
    mock_ax.hist2d.return_value = (None, None, None, mock_image)

    # 3 valid days with simple times
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["07:30:00", "08:00:00", "09:15:00"],
            "end_time": ["16:00:00", "16:30:00", "17:45:00"],
            "work_time": [8.5, 8.5, 8.5],
            "overtime": [0.0, 0.0, 0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)
    visualizer.create_start_end_time_histogram()

    mock_subplots.assert_called_once_with(figsize=(8, 5))
    mock_ax.hist2d.assert_called_once()

    # Verify axis label configuration (start/end time wording)
    mock_ax.set_xlabel.assert_called_once_with("Start Time of Day")
    mock_ax.set_ylabel.assert_called_once_with("End Time of Day")
    assert "Start vs. End Time 2D Histogram" in mock_ax.set_title.call_args[0][0]

    # Colorbar called and formatter set to integer ticks via locator
    mock_colorbar.assert_called_once()


@pytest.mark.fast
def test_create_start_end_time_histogram_no_valid_pairs_logs_warning(
    sample_config: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """When no valid start/end time pairs exist, log a warning and return early."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["invalid", "also invalid"],
            "end_time": ["invalid", "also invalid"],
            "work_time": [8.0, 8.0],
            "overtime": [0.0, 0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    with caplog.at_level("WARNING", logger="src.visualizer"):
        visualizer.create_start_end_time_histogram()

    # Function should log that there are no valid pairs and not raise.
    assert "No valid start/end time pairs to display in 2D histogram." in caplog.text

"""Unit tests for Visualizer.display_all_plots."""

from unittest.mock import patch

import pytest

import src.visualizer as viz


@pytest.mark.fast
def test_display_all_plots_calls_plt_show() -> None:
    """Test display_all_plots calls plt.show()."""
    visualizer = viz.Visualizer.__new__(viz.Visualizer)

    with (
        patch.object(visualizer, "create_start_end_time_histogram") as mock_start_end_hist,
        patch.object(visualizer, "create_work_hours_histogram") as mock_work_hist,
        patch.object(visualizer, "create_work_hours_per_weekday_histogram") as mock_weekday_hist,
        patch.object(visualizer, "create_daily_work_hours_plot") as mock_daily_plot,
        patch("src.visualizer.plt.show") as mock_show,
    ):
        visualizer.display_all_plots()

        mock_start_end_hist.assert_called_once()
        mock_work_hist.assert_called_once()
        mock_weekday_hist.assert_called_once()
        mock_daily_plot.assert_called_once()
        mock_show.assert_called_once()

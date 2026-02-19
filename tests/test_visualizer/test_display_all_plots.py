"""Unit tests for the Visualizer display_all_plots static method."""

from unittest.mock import patch

import pytest

import src.visualizer as viz


@pytest.mark.fast
@patch("src.visualizer.plt.show")
def test_display_all_plots_calls_plt_show(mock_show: patch) -> None:
    """Test display_all_plots calls plt.show() (line 294)."""
    viz.Visualizer.display_all_plots()
    mock_show.assert_called_once()

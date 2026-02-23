"""Unit tests for the Visualizer display_all_plots static method."""

from unittest.mock import patch

import pytest

import src.visualizer as viz


@pytest.mark.fast
def test_display_all_plots_calls_plt_show() -> None:
    """Test display_all_plots calls plt.show() (line 294)."""
    with patch("src.visualizer.plt.show") as mock_show:
        viz.Visualizer.display_all_plots()
        mock_show.assert_called_once()

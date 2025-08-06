"""Tests for the tail method in the Logbook class."""

from unittest.mock import patch

import pandas as pd
import pytest

from src.logbook import Logbook


@pytest.mark.fast
def test_tail_default_parameter(logbook: Logbook, sample_logbook_df: pd.DataFrame) -> None:
    """Test tail method with default parameter (n=4)."""
    logbook.save_logbook(sample_logbook_df)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should contain last 4 rows (default)
        assert "Wed" in logged_output
        assert "Thu" in logged_output
        assert "Fri" in logged_output
        assert "Mon" not in logged_output  # First row should not be in last 4


@pytest.mark.fast
def test_tail_custom_parameter(logbook: Logbook, sample_logbook_df: pd.DataFrame) -> None:
    """Test tail method with custom parameter (n=2)."""
    logbook.save_logbook(sample_logbook_df)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail(n=2)
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should contain only last 2 rows
        assert len(logged_output.split("\n")) == 3  # 2 rows of content plus one row for the header
        assert "Thu" in logged_output
        assert "Fri" in logged_output
        assert "Wed" not in logged_output


@pytest.mark.fast
def test_tail_empty_dataframe(logbook: Logbook) -> None:
    """Test tail method with empty DataFrame."""
    empty_df = pd.DataFrame(
        columns=["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"],
    )
    logbook.save_logbook(empty_df)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        assert not logged_output.strip() or "weekday" in logged_output


@pytest.mark.fast
def test_tail_n_larger_than_dataframe(logbook: Logbook, sample_logbook_df: pd.DataFrame) -> None:
    """Test tail method when n is larger than DataFrame size."""
    logbook.save_logbook(sample_logbook_df)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail(n=10)  # n > number of rows (5)
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should contain all rows since n > dataframe size
        assert "Mon" in logged_output
        assert "Tue" in logged_output
        assert "Wed" in logged_output
        assert "Thu" in logged_output
        assert "Fri" in logged_output

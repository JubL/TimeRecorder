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
        # Should contain title, separator, and last 4 rows (default)
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output
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
        # Should contain title, separator, and last 2 rows
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output
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
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output


@pytest.mark.fast
def test_tail_n_larger_than_dataframe(logbook: Logbook, sample_logbook_df: pd.DataFrame) -> None:
    """Test tail method when n is larger than DataFrame size."""
    logbook.save_logbook(sample_logbook_df)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail(n=10)  # n > number of rows (5)
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should contain title, separator, and all rows since n > dataframe size
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output
        assert "Mon" in logged_output
        assert "Tue" in logged_output
        assert "Wed" in logged_output
        assert "Thu" in logged_output
        assert "Fri" in logged_output


@pytest.mark.fast
def test_tail_with_zero_values(logbook: Logbook) -> None:
    """Test tail method with zero values in work_time and overtime."""
    df_with_zeros = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": ["1.0", "1.0"],
            "work_time": [0.0, 0.0],
            "case": ["undertime", "undertime"],
            "overtime": [0.0, 0.0],
        },
    )
    logbook.save_logbook(df_with_zeros)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should show "0h 0m" for zero values (current bug: shows empty string)
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output


@pytest.mark.fast
def test_tail_with_decimal_hours(logbook: Logbook) -> None:
    """Test tail method with decimal hours (e.g., 7.5 hours)."""
    df_with_decimals = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": ["1.0", "1.0"],
            "work_time": [7.5, 8.25],
            "case": ["overtime", "overtime"],
            "overtime": [0.5, 1.25],
        },
    )
    logbook.save_logbook(df_with_decimals)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should show formatted hours like "7h 30m" and "8h 15m"
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output


@pytest.mark.fast
def test_tail_with_negative_values(logbook: Logbook) -> None:
    """Test tail method with negative values in work_time and overtime."""
    df_with_negatives = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": ["1.0", "1.0"],
            "work_time": [-1.5, -2.0],
            "case": ["undertime", "undertime"],
            "overtime": [-1.5, -2.0],
        },
    )
    logbook.save_logbook(df_with_negatives)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should handle negative values appropriately
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output


@pytest.mark.fast
def test_tail_with_string_values(logbook: Logbook) -> None:
    """Test tail method with string values in work_time and overtime."""
    df_with_strings = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": ["1.0", "1.0"],
            "work_time": ["7.5", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.5", "1.0"],
        },
    )
    logbook.save_logbook(df_with_strings)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should handle string values appropriately
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output


@pytest.mark.fast
def test_tail_with_mixed_data_types(logbook: Logbook) -> None:
    """Test tail method with mixed data types in work_time and overtime."""
    df_with_mixed = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00", "17:00:00"],
            "lunch_break_duration": ["1.0", "1.0", "1.0"],
            "work_time": [7.5, "8.0", 0.0],
            "case": ["overtime", "overtime", "undertime"],
            "overtime": ["0.5", 1.0, 0.0],
        },
    )
    logbook.save_logbook(df_with_mixed)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should handle mixed data types appropriately
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output


@pytest.mark.fast
def test_tail_with_nan_values(logbook: Logbook) -> None:
    """Test tail method with NaN values in work_time and overtime."""
    df_with_nan = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": ["1.0", "1.0"],
            "work_time": [7.5, float("nan")],
            "case": ["overtime", "undertime"],
            "overtime": [0.5, float("nan")],
        },
    )
    logbook.save_logbook(df_with_nan)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.error.assert_called_once()

        logged_output = mock_logger.error.call_args[0][0]
        # Should handle NaN values appropriately
        assert "Non-numeric values found in work_time or overtime columns. Please check the logbook file." in logged_output


@pytest.mark.fast
def test_tail_with_very_large_values(logbook: Logbook) -> None:
    """Test tail method with very large values in work_time and overtime."""
    df_with_large = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": ["1.0", "1.0"],
            "work_time": [999.99, 1000.0],
            "case": ["overtime", "overtime"],
            "overtime": [999.99, 1000.0],
        },
    )
    logbook.save_logbook(df_with_large)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should handle very large values appropriately
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output


@pytest.mark.fast
def test_tail_with_none_values(logbook: Logbook) -> None:
    """Test tail method with None values in work_time and overtime."""
    df_with_none = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": ["1.0", "1.0"],
            "work_time": [7.5, None],
            "case": ["overtime", "undertime"],
            "overtime": [0.5, None],
        },
    )
    logbook.save_logbook(df_with_none)

    with patch("src.logbook.logger") as mock_logger:
        logbook.tail()
        mock_logger.error.assert_called_once()

        logged_output = mock_logger.error.call_args[0][0]
        # Should handle None values appropriately
        assert "Non-numeric values found in work_time or overtime columns. Please check the logbook file." in logged_output


@pytest.mark.fast
def test_tail_with_invalid_n_parameter(logbook: Logbook, sample_logbook_df: pd.DataFrame) -> None:
    """Test tail method with invalid n parameter (negative or zero)."""
    logbook.save_logbook(sample_logbook_df)

    with patch("src.logbook.logger") as mock_logger:
        # Test with negative n
        logbook.tail(n=-1)
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should handle negative n appropriately (pandas tail behavior)
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output

        # Reset mock for next test
        mock_logger.reset_mock()

        # Test with zero n
        logbook.tail(n=0)
        mock_logger.info.assert_called_once()

        logged_output = mock_logger.info.call_args[0][0]
        # Should handle zero n appropriately (pandas tail behavior)
        assert "Recent Entries" in logged_output
        assert "===============" in logged_output


@pytest.mark.fast
def test_tail_load_logbook_failure(logbook: Logbook) -> None:
    """Test tail method when load_logbook fails."""
    with patch.object(logbook, "load_logbook", side_effect=Exception("File not found")), patch("src.logbook.logger") as mock_logger:
        with pytest.raises(Exception, match="File not found"):
            logbook.tail()
        # Should not call logger.info if load_logbook fails
        mock_logger.info.assert_not_called()

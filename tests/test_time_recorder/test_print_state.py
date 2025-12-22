"""Unit tests for the TimeRecorder print_state method."""

from unittest.mock import patch

import pytest

import src.time_recorder as tr


@pytest.mark.fast
def test_print_state_calls_logger_info() -> None:
    """Test that print_state calls logger.info with the TimeRecorder object."""
    # Create a TimeRecorder instance
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:00",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    # Mock the logger.info method
    with patch.object(tr.logger, "info") as mock_info:
        line.print_state()
        # Verify logger.info was called once with the TimeRecorder object
        mock_info.assert_called_once_with(line)


@pytest.mark.fast
def test_print_state_logs_string_representation() -> None:
    """Test that print_state logs the string representation of the TimeRecorder."""
    # Create a TimeRecorder instance
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "17:30",  # 9.5 hours total, 1 hour lunch = 8.5 hours work (overtime)
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    # Mock the logger.info method
    with patch.object(tr.logger, "info") as mock_info:
        line.print_state()
        # Verify logger.info was called with the TimeRecorder object
        # The logger will convert it to string via __str__
        call_args = mock_info.call_args[0]
        assert len(call_args) == 1
        assert call_args[0] == line
        # Verify the string representation contains expected content
        str_repr = str(line)
        assert "Time Recorder - Work Hours Calculator" in str_repr
        assert "24.04.2025" in str_repr


@pytest.mark.fast
def test_print_state_with_different_cases() -> None:
    """Test print_state works with both overtime and undertime cases."""
    # Test with overtime case
    line_overtime = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "17:30",  # Overtime
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    with patch.object(tr.logger, "info") as mock_info:
        line_overtime.print_state()
        mock_info.assert_called_once_with(line_overtime)

    # Test with undertime case
    line_undertime = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:30",  # Undertime
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    with patch.object(tr.logger, "info") as mock_info:
        line_undertime.print_state()
        mock_info.assert_called_once_with(line_undertime)

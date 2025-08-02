"""Unit tests for the time_recording module, including TimeRecorder and related functionality."""

import pandas as pd
import pytest

import src.logbook as lb


@pytest.mark.fast
def test_returns_zero_if_no_work_days(logbook: lb.Logbook, caplog: pytest.LogCaptureFixture) -> None:
    """Should return 0.0 and a log warning if no work days are found (all work_time zero)."""
    logbook.create_df()
    with caplog.at_level("WARNING"):
        logbook.get_weekly_hours_from_log()
        assert "No work days found in the log file." in caplog.text


@pytest.mark.fast
def test_returns_expected_weekly_hours(logbook: lb.Logbook, caplog: pytest.LogCaptureFixture) -> None:
    """Should return correct weekly hours for valid log file."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "date": ["2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24", "2025-04-25"],
            "start_time": ["08:00", "08:00", "08:00", "08:00", "08:00"],
            "end_time": ["17:00", "16:30", "17:00", "17:30", "17:00"],
            "lunch_break_duration": [60, 60, 60, 60, 60],
            "work_time": [8, 7.5, 8, 8.5, 8],  # hours
            "case": ["", "", "", "", ""],
            "overtime": ["", "", "", "", ""],
        },
    )
    logbook.save_logbook(df)
    # Average per day = (8 + 7.5 + 8 + 8.5 + 8) / 5 = 8.0, so weekly = 8.0 * 5 = 40.0
    with caplog.at_level("INFO"):
        logbook.get_weekly_hours_from_log()
        assert "Average weekly hours: 40.0 hours" in caplog.text


@pytest.mark.fast
def test_ignores_zero_work_time_days(logbook: lb.Logbook, caplog: pytest.LogCaptureFixture) -> None:
    """Should only average over days with work_time > 0."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "date": ["2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24", "2025-04-25"],
            "start_time": ["08:00", "", "08:00", "", "08:00"],
            "end_time": ["16:00", "", "16:00", "", "16:00"],
            "lunch_break_duration": [60, 60, 60, 60, 60],
            "work_time": [8, 0, 8, 0, 8],  # Only 3 days with work
            "case": ["", "", "", "", ""],
            "overtime": [0, "", 0, "", 0],
        },
    )
    logbook.save_logbook(df)
    # Average per day = (8+8+8)/3 = 8.0, weekly = 8.0*5 = 40.0
    with caplog.at_level("INFO"):
        logbook.get_weekly_hours_from_log()
        assert "Average weekly hours: 40.0 hours" in caplog.text


@pytest.mark.fast
def test_handles_non_numeric_work_time(logbook: lb.Logbook, caplog: pytest.LogCaptureFixture) -> None:
    """Should log error and return 0.0 if work_time cannot be converted."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": ["2025-04-21"],
            "start_time": ["08:00"],
            "end_time": ["16:00"],
            "lunch_break_duration": [60],
            "work_time": ["not_a_number"],
            "case": [""],
            "overtime": [""],
        },
    )
    logbook.save_logbook(df)
    with caplog.at_level("ERROR"):
        logbook.get_weekly_hours_from_log()
        assert "Error converting 'work_time' to timedelta" in caplog.text


@pytest.mark.fast
def test_rounds_to_two_decimals(logbook: lb.Logbook, caplog: pytest.LogCaptureFixture) -> None:
    """Should round the result to two decimal places."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["2025-04-21", "2025-04-22"],
            "start_time": ["08:00", "08:00"],
            "end_time": ["15:20", "16:00"],  # 7.3333 and 7.6666 hours
            "lunch_break_duration": [60, 60],
            "work_time": [7.3333, 7.6666],
            "case": ["undertime", "undertime"],
            "overtime": ["", ""],
        },
    )
    logbook.save_logbook(df)
    # The average of (7.3333 + 7.6666) / 2 is 7.5, weekly = 7.5*5 = 37.5
    with caplog.at_level("INFO"):
        logbook.get_weekly_hours_from_log()
        assert "Average weekly hours: 37.5 hours" in caplog.text

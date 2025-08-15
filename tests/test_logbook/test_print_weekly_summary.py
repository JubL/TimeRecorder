"""Unit tests for the print_weekly_summary method in the Logbook class."""

import pathlib

import pandas as pd
import pytest

import src.logbook as lb


@pytest.mark.fast
def test_print_weekly_summary_with_fractional_standard_hours(tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
    """Should handle fractional standard work hours correctly."""
    # Create a logbook with fractional standard work hours (7.5 hours)
    log_file = tmp_path / "log.csv"
    logbook = lb.Logbook(
        data={
            "log_path": log_file,
            "full_format": "%d.%m.%Y %H:%M:%S",
            "holidays": "DE",
            "subdivision": "HE",
            "standard_work_hours": 7.5,  # Fractional hours to test line 553
            "work_days": [0, 1, 2, 3, 4],
        },
    )

    # Create test data
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "date": ["2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24", "2025-04-25"],
            "start_time": ["08:00", "08:00", "08:00", "08:00", "08:00"],
            "end_time": ["17:00", "16:30", "17:00", "17:30", "17:00"],
            "lunch_break_duration": [60, 60, 60, 60, 60],
            "work_time": [8, 7.5, 8, 8.5, 8],  # hours
            "case": ["overtime", "overtime", "overtime", "overtime", "overtime"],
            "overtime": [0.5, 0.0, 0.5, 1.0, 0.5],
        },
    )
    logbook.save_logbook(df)

    # Test print_weekly_summary with fractional standard hours
    with caplog.at_level("INFO"):
        logbook.print_weekly_summary()

        # Check that the output contains the expected format for fractional standard hours
        assert "Standard Hours: 37h 30m" in caplog.text  # 7.5 * 5 = 37.5 hours
        assert "Average Weekly Hours:" in caplog.text
        assert "Mean Daily Overtime:" in caplog.text


@pytest.mark.fast
def test_print_weekly_summary_with_whole_standard_hours(logbook: lb.Logbook, caplog: pytest.LogCaptureFixture) -> None:
    """Should handle whole number standard work hours correctly."""
    # Create test data
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "date": ["2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24", "2025-04-25"],
            "start_time": ["08:00", "08:00", "08:00", "08:00", "08:00"],
            "end_time": ["17:00", "16:30", "17:00", "17:30", "17:00"],
            "lunch_break_duration": [60, 60, 60, 60, 60],
            "work_time": [8, 7.5, 8, 8.5, 8],  # hours
            "case": ["overtime", "undertime", "overtime", "overtime", "overtime"],
            "overtime": [0.0, -0.5, 0.0, 0.5, 0.0],
        },
    )
    logbook.save_logbook(df)

    # Test print_weekly_summary with whole number standard hours
    with caplog.at_level("INFO"):
        logbook.print_weekly_summary()

        # Check that the output contains the expected format for whole number standard hours
        assert "Standard Hours: 40h" in caplog.text  # 8 * 5 = 40 hours (no minutes)
        assert "Average Weekly Hours:" in caplog.text
        assert "Mean Daily Overtime:" in caplog.text


@pytest.mark.fast
def test_print_weekly_summary_with_zero_work_days(logbook: lb.Logbook, caplog: pytest.LogCaptureFixture) -> None:
    """Should handle empty logbook gracefully."""
    # Create empty DataFrame
    df = pd.DataFrame(columns=["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"])
    logbook.save_logbook(df)

    # Test print_weekly_summary with empty data
    with caplog.at_level("INFO"):
        logbook.print_weekly_summary()

        # Check that the output contains the expected format
        assert "Standard Hours: 40h" in caplog.text
        assert "Average Weekly Hours: 0h 0m" in caplog.text
        assert "Mean Daily Overtime: 0h 0m" in caplog.text


@pytest.mark.fast
def test_print_weekly_summary_with_fractional_standard_hours_8_5(tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
    """Should handle another fractional standard work hours value (8.5 hours)."""
    # Create a logbook with 8.5 hour standard work day
    log_file = tmp_path / "log.csv"
    logbook = lb.Logbook(
        data={
            "log_path": log_file,
            "full_format": "%d.%m.%Y %H:%M:%S",
            "holidays": "DE",
            "subdivision": "HE",
            "standard_work_hours": 8.5,  # Another fractional value
            "work_days": [0, 1, 2, 3, 4],
        },
    )

    # Create test data
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["2025-04-21", "2025-04-22"],
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": [60, 60],
            "work_time": [8, 8],
            "case": ["undertime", "undertime"],
            "overtime": [-0.5, -0.5],
        },
    )
    logbook.save_logbook(df)

    # Test print_weekly_summary with 8.5 hour standard day
    with caplog.at_level("INFO"):
        logbook.print_weekly_summary()

        # Check that the output contains the expected format for 8.5 hour standard day
        assert "Standard Hours: 42h 30m" in caplog.text  # 8.5 * 5 = 42.5 hours
        assert "Average Weekly Hours:" in caplog.text
        assert "Mean Daily Overtime:" in caplog.text

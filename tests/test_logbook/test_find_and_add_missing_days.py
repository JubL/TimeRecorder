"""Tests for the find_and_add_missing_days method in logbook.py."""

import pandas as pd
import pytest

import src.logbook as lb


@pytest.mark.fast
def test_find_and_add_missing_days_with_missing_days(logbook: lb.Logbook) -> None:
    """Test that find_and_add_missing_days calls the appropriate methods when missing days are found."""
    # Create a logbook with a gap that includes weekend days
    df = pd.DataFrame(
        {
            "weekday": ["Fri", "Mon"],  # Gap includes Saturday and Sunday
            "date": ["05.01.2024", "08.01.2024"],  # Fri to Mon (Sat is 06.01.2024, Sun is 07.01.2024)
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": [60, 60],
            "work_time": [8.0, 8.0],
            "case": ["overtime", "overtime"],
            "overtime": [0.0, 0.0],
        },
    )

    logbook.save_logbook(df)

    logbook.find_and_add_missing_days()

    # Verify that missing days were added
    result = logbook.load_logbook()
    assert len(result) == 4  # Original 2 + Saturday + Sunday

    # Check that Saturday and Sunday were added
    saturday_row = result[result["date"] == "06.01.2024"].iloc[0]
    assert saturday_row["weekday"] == "Sat"
    # pandas converts "0" to 0.0 when reading CSV, so we need to check for either
    assert saturday_row["work_time"] in {"0", 0.0}

    sunday_row = result[result["date"] == "07.01.2024"].iloc[0]
    assert sunday_row["weekday"] == "Sun"
    # pandas converts "0" to 0.0 when reading CSV, so we need to check for either
    assert sunday_row["work_time"] in {"0", 0.0}


@pytest.mark.fast
def test_find_and_add_missing_days_with_no_missing_days(logbook: lb.Logbook) -> None:
    """Test that find_and_add_missing_days does nothing when no missing days are found."""
    # Create a logbook with consecutive days (no gaps)
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00", "17:00:00"],
            "lunch_break_duration": [60, 60, 60],
            "work_time": [8.0, 8.0, 8.0],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": [0.0, 0.0, 0.0],
        },
    )

    logbook.save_logbook(df)

    logbook.find_and_add_missing_days()

    # Verify that no days were added
    result = logbook.load_logbook()
    assert len(result) == 3  # Original 3 entries, no additions


@pytest.mark.fast
def test_find_and_add_missing_days_with_empty_logbook(logbook: lb.Logbook) -> None:
    """Test that find_and_add_missing_days handles empty logbook gracefully."""
    logbook.create_df()
    logbook.find_and_add_missing_days()
    # Verify that the logbook is still empty
    result = logbook.load_logbook()
    assert len(result) == 0


@pytest.mark.fast
def test_find_and_add_missing_days_with_single_entry(logbook: lb.Logbook) -> None:
    """Test that find_and_add_missing_days handles single entry logbook."""
    # Create a logbook with only one entry
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "end_time": ["17:00:00"],
            "lunch_break_duration": [60],
            "work_time": [8.0],
            "case": ["overtime"],
            "overtime": [0.0],
        },
    )

    logbook.save_logbook(df)

    logbook.find_and_add_missing_days()

    # Verify that the logbook still has only one entry
    result = logbook.load_logbook()
    assert len(result) == 1

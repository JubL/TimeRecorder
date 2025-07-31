"""Unit tests for the time_recording module, including TimeRecorder and related functionality."""

import pathlib

import pandas as pd
import pytest

import src.logbook as lb


@pytest.fixture
def logbook(tmp_path: pathlib.Path) -> lb.Logbook:
    """Fixture to create a sample Logbook for testing."""
    return lb.Logbook(log_path=tmp_path / "log.csv")


@pytest.mark.fast
def test_squash_df_groups_and_sums_correctly(logbook: lb.Logbook, tmp_path: pathlib.Path) -> None:
    """Test that squash_df groups by date and sums work_time and lunch_break_duration."""
    df_file = tmp_path / "log.csv"
    # Create a DataFrame with duplicate dates and different work_time/lunch_break_duration
    df = pd.DataFrame(
        {
            "weekday": ["Thu", "Thu", "Fri"],
            "date": ["24.04.2025", "24.04.2025", "25.04.2025"],
            "start_time": ["08:00:00", "11:30:00", "08:00:00"],
            "end_time": ["9:00:00", "17:00:00", "16:00:00"],
            "lunch_break_duration": [1, 60, 60],
            "work_time": [1.0, 6.0, 8.0],
            "case": ["undertime", "undertime", "overtime"],
            "overtime": [-7, 4.5, 0.0],
        },
    )
    df.to_csv(df_file, sep=";", index=False, encoding="utf-8")  # TODO replace with logbook.save_logbook(df)?
    logbook.squash_df()
    result = pd.read_csv(df_file, sep=";", encoding="utf-8")
    # Should have two rows (grouped by date and weekday)
    assert len(result) == 2
    # Check that lunch_break_duration and work_time are summed for the grouped date
    grouped = result[result["date"] == "24.04.2025"]
    assert not grouped.empty, "No rows found for date '24.04.2025'"
    assert grouped.iloc[0]["lunch_break_duration"] == 61  # 1 + 60
    assert grouped.iloc[0]["work_time"] == 7  # 1.0 + 6.0
    # Check that start_time is 'first' and end_time is 'last'
    assert grouped.iloc[0]["start_time"] == "08:00:00"
    assert grouped.iloc[0]["end_time"] == "17:00:00"

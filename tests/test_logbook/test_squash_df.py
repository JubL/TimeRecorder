"""Comprehensive unit tests for the squash_df method in logbook.py."""

import pandas as pd
import pytest

import src.logbook as lb


@pytest.mark.fast
def test_squash_df_groups_by_date_and_weekday(logbook: lb.Logbook, sample_df: pd.DataFrame) -> None:
    """Test that squash_df correctly groups entries by date and weekday."""
    logbook.save_logbook(sample_df)

    logbook.squash_df()

    result = logbook.load_logbook()

    # Should have 2 rows (grouped by unique date + weekday combinations)
    assert len(result) == 2

    # Check that we have one row for each unique date
    unique_dates = result["date"].unique()
    assert len(unique_dates) == 2
    assert "24.04.2025" in unique_dates
    assert "25.04.2025" in unique_dates


@pytest.mark.fast
def test_squash_df_sums_work_time_and_lunch_break(logbook: lb.Logbook, sample_df: pd.DataFrame, relative_precision: float) -> None:
    """Test that squash_df correctly sums work_time and lunch_break_duration."""
    logbook.save_logbook(sample_df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Check Monday's data (3 entries)
    monday_row = result[result["date"] == "24.04.2025"].iloc[0]
    assert monday_row["work_time"] == pytest.approx(5.75, rel=relative_precision)  # 1.5 + 1.25 + 3.0
    assert monday_row["lunch_break_duration"] == 135  # 30 + 45 + 60

    # Check Tuesday's data (2 entries)
    tuesday_row = result[result["date"] == "25.04.2025"].iloc[0]
    assert tuesday_row["work_time"] == pytest.approx(8.0, rel=relative_precision)  # 4.0 + 4.0
    assert tuesday_row["lunch_break_duration"] == 90  # 60 + 30


@pytest.mark.fast
def test_squash_df_takes_first_start_time_and_last_end_time(logbook: lb.Logbook, sample_df: pd.DataFrame) -> None:
    """Test that squash_df takes first start_time and last end_time for each group."""
    logbook.save_logbook(sample_df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Check Monday's data
    monday_row = result[result["date"] == "24.04.2025"].iloc[0]
    assert monday_row["start_time"] == "08:00:00"  # First start time
    assert monday_row["end_time"] == "17:00:00"  # Last end time

    # Check Tuesday's data
    tuesday_row = result[result["date"] == "25.04.2025"].iloc[0]
    assert tuesday_row["start_time"] == "08:00:00"  # First start time
    assert tuesday_row["end_time"] == "17:00:00"  # Last end time


@pytest.mark.fast
def test_squash_df_recalculates_case_and_overtime(logbook: lb.Logbook, sample_df: pd.DataFrame, relative_precision: float) -> None:
    """Test that squash_df recalculates case and overtime based on summed work_time."""
    logbook.save_logbook(sample_df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Check Monday's data (5.75 hours total - should be undertime)
    monday_row = result[result["date"] == "24.04.2025"].iloc[0]
    assert monday_row["case"] == "undertime"
    assert monday_row["overtime"] == pytest.approx(-2.25, rel=relative_precision)  # 5.75 - 8.0 = -2.25

    # Check Tuesday's data (8.0 hours total - should be overtime)
    tuesday_row = result[result["date"] == "25.04.2025"].iloc[0]
    assert tuesday_row["case"] == "overtime"
    assert tuesday_row["overtime"] == pytest.approx(0.0, rel=relative_precision)  # 8.0 - 8.0 = 0.0


@pytest.mark.fast
def test_squash_df_preserves_column_order(logbook: lb.Logbook, sample_df: pd.DataFrame) -> None:
    """Test that squash_df preserves the correct column order."""
    logbook.save_logbook(sample_df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Check column order
    expected_columns = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
    assert list(result.columns) == expected_columns


@pytest.mark.fast
def test_squash_df_formats_dates_correctly(logbook: lb.Logbook, sample_df: pd.DataFrame) -> None:
    """Test that squash_df formats dates according to the date_format."""
    logbook.save_logbook(sample_df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Check that dates are formatted correctly
    for date in result["date"]:
        # Should be in DD.MM.YYYY format
        assert len(date.split(".")) == 3
        day, month, year = date.split(".")
        assert len(day) == 2
        assert len(month) == 2
        assert len(year) == 4


@pytest.mark.fast
def test_squash_df_with_single_entry(logbook: lb.Logbook, relative_precision: float) -> None:
    """Test that squash_df works correctly with a single entry (no grouping needed)."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": ["24.04.2025"],
            "start_time": ["08:00:00"],
            "end_time": ["17:00:00"],
            "lunch_break_duration": [60],
            "work_time": [8.0],
            "case": ["overtime"],
            "overtime": [0.0],
        },
    )

    logbook.save_logbook(df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Should have one row unchanged
    assert len(result) == 1
    row = result.iloc[0]
    assert row["work_time"] == pytest.approx(8.0, rel=relative_precision)
    assert row["lunch_break_duration"] == 60
    assert row["case"] == "overtime"
    assert row["overtime"] == pytest.approx(0.0, rel=relative_precision)


@pytest.mark.fast
def test_squash_df_with_multiple_dates(logbook: lb.Logbook, relative_precision: float) -> None:
    """Test that squash_df works correctly with multiple different dates."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon", "Tue", "Tue", "Wed"],
            "date": ["24.04.2025", "24.04.2025", "25.04.2025", "25.04.2025", "26.04.2025"],
            "start_time": ["08:00:00", "11:00:00", "08:00:00", "13:00:00", "08:00:00"],
            "end_time": ["10:00:00", "17:00:00", "12:00:00", "17:00:00", "17:00:00"],
            "lunch_break_duration": [30, 60, 60, 30, 60],
            "work_time": [1.5, 5.5, 4.0, 4.0, 8.0],
            "case": ["undertime", "undertime", "undertime", "undertime", "overtime"],
            "overtime": [-6.5, -2.5, -4.0, -4.0, 0.0],
        },
    )

    logbook.save_logbook(df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Should have 3 rows (one for each unique date)
    assert len(result) == 3

    # Check each date's data
    monday = result[result["date"] == "24.04.2025"].iloc[0]
    assert monday["work_time"] == pytest.approx(7.0, rel=relative_precision)  # 1.5 + 5.5
    assert monday["lunch_break_duration"] == 90  # 30 + 60
    assert monday["case"] == "undertime"  # 7.0 < 8.0

    tuesday = result[result["date"] == "25.04.2025"].iloc[0]
    assert tuesday["work_time"] == pytest.approx(8.0, rel=relative_precision)  # 4.0 + 4.0
    assert tuesday["lunch_break_duration"] == 90  # 60 + 30
    assert tuesday["case"] == "overtime"  # 8.0 == 8.0

    wednesday = result[result["date"] == "26.04.2025"].iloc[0]
    assert wednesday["work_time"] == pytest.approx(8.0, rel=relative_precision)
    assert wednesday["lunch_break_duration"] == 60
    assert wednesday["case"] == "overtime"  # 8.0 == 8.0


@pytest.mark.fast
def test_squash_df_edge_case_overtime_threshold(logbook: lb.Logbook, relative_precision: float) -> None:
    """Test that squash_df correctly handles the overtime threshold (8 hours)."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon"],
            "date": ["24.04.2025", "24.04.2025"],
            "start_time": ["08:00:00", "13:00:00"],
            "end_time": ["12:00:00", "17:00:00"],
            "lunch_break_duration": [60, 60],
            "work_time": [3.0, 4.99],  # Total: 7.99 (undertime)
            "case": ["undertime", "undertime"],
            "overtime": [-5.0, -3.01],
        },
    )

    logbook.save_logbook(df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Should be undertime (7.99 < 8.0)
    row = result.iloc[0]
    assert row["work_time"] == pytest.approx(7.99, rel=relative_precision)
    assert row["case"] == "undertime"
    assert row["overtime"] == pytest.approx(-0.01, rel=relative_precision)  # 7.99 - 8.0 = -0.01


@pytest.mark.fast
def test_squash_df_exactly_8_hours(logbook: lb.Logbook, relative_precision: float) -> None:
    """Test that squash_df correctly handles exactly 8 hours (overtime threshold)."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon"],
            "date": ["24.04.2025", "24.04.2025"],
            "start_time": ["08:00:00", "13:00:00"],
            "end_time": ["12:00:00", "17:00:00"],
            "lunch_break_duration": [60, 60],
            "work_time": [4.0, 4.0],  # Total: 8.0 (exactly overtime threshold)
            "case": ["undertime", "undertime"],
            "overtime": [-4.0, -4.0],
        },
    )

    logbook.save_logbook(df)

    logbook.squash_df()
    result = logbook.load_logbook()

    # Should be overtime (8.0 >= 8.0)
    row = result.iloc[0]
    assert row["work_time"] == pytest.approx(8.0, rel=relative_precision)
    assert row["case"] == "overtime"
    assert row["overtime"] == pytest.approx(0.0, rel=relative_precision)  # 8.0 - 8.0 = 0.0


@pytest.mark.fast
def test_squash_df_groups_and_sums_correctly(logbook: lb.Logbook, relative_precision: float) -> None:
    """Test that squash_df groups by date and sums work_time and lunch_break_duration."""
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
    logbook.save_logbook(df)
    logbook.squash_df()
    result = logbook.load_logbook()
    # Should have two rows (grouped by date and weekday)
    assert len(result) == 2
    # Check that lunch_break_duration and work_time are summed for the grouped date
    grouped = result[result["date"] == "24.04.2025"]
    assert not grouped.empty, "No rows found for date '24.04.2025'"
    assert grouped.iloc[0]["lunch_break_duration"] == 61  # 1 + 60
    assert grouped.iloc[0]["work_time"] == pytest.approx(7.0, rel=relative_precision)  # 1.0 + 6.0
    # Check that start_time is 'first' and end_time is 'last'
    assert grouped.iloc[0]["start_time"] == "08:00:00"
    assert grouped.iloc[0]["end_time"] == "17:00:00"


@pytest.mark.fast
def test_squash_df_missing_work_time(logbook: lb.Logbook) -> None:
    """Test that squash_df handles missing/empty work_time correctly (line 343)."""
    # Create a DataFrame with missing work_time values
    df_with_missing_work_time = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["24.04.2025", "25.04.2025", "26.04.2025"],
            "start_time": ["08:00:00", "09:00:00", "08:30:00"],
            "end_time": ["17:00:00", "18:00:00", "17:30:00"],
            "lunch_break_duration": [30, 45, 60],
            "work_time": ["", pd.NA, 8.0],  # Missing/empty work_time values
            "case": ["overtime", "overtime", "overtime"],
            "overtime": [0.5, 0.25, 0.0],
        },
    )

    # Save the DataFrame to the logbook file
    logbook.save_logbook(df_with_missing_work_time)

    # Test that squash_df handles missing work_time without errors
    # The process_work_time_row function should return ("", "") for missing work_time
    logbook.squash_df()

    # Verify the result was saved correctly
    result_df = logbook.load_logbook()
    assert len(result_df) > 0  # Should have processed the data without errors

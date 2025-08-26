import logging
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

import src.logbook as lb


@pytest.mark.fast
def test_add_missing_days_empty_missing_days(logbook: lb.Logbook) -> None:
    """Test that add_missing_days_to_logbook handles empty missing_days list."""
    # Create a logbook with some data
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Wed"],
            "date": ["01.01.2024", "03.01.2024"],
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["8.0", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.0"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Call with empty missing_days list
    logbook.add_missing_days_to_logbook([])

    # Verify the logbook is unchanged
    result_df = logbook.load_logbook()
    assert len(result_df) == 2
    assert list(result_df["date"]) == ["01.01.2024", "03.01.2024"]


@pytest.mark.fast
def test_add_missing_days_saturday(logbook: lb.Logbook, relative_precision: float) -> None:
    """Test that add_missing_days_to_logbook adds missing Saturday."""
    # Create a logbook with gap that includes a Saturday
    df = pd.DataFrame(
        {
            "weekday": ["Fri", "Mon"],  # Gap includes Saturday
            "date": ["05.01.2024", "08.01.2024"],  # Fri to Mon (Sat is 06.01.2024)
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": [60, 60],
            "work_time": [8.0, 8.0],
            "case": ["overtime", "overtime"],
            "overtime": [0.0, 0.0],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Missing days: Fri to Mon (should add Saturday and Sunday)
    missing_days = [(datetime(2024, 1, 5), datetime(2024, 1, 8))]

    with patch("src.logbook.logger") as mock_logger:
        logbook.add_missing_days_to_logbook(missing_days)

        # Verify Saturday and Sunday were added
        result_df = logbook.load_logbook()
        assert len(result_df) == 4  # Original 2 work days+ 2 weekend days

        # Check that Saturday was added with correct format
        saturday_row = result_df[result_df["date"] == "06.01.2024"].iloc[0]
        assert saturday_row["weekday"] == "Sat"
        assert not saturday_row["start_time"]
        assert not saturday_row["end_time"]
        assert not saturday_row["lunch_break_duration"]
        assert saturday_row["work_time"] == pytest.approx(0.0, rel=relative_precision)
        assert not saturday_row["case"]
        assert not saturday_row["overtime"]

        # Verify logging
        mock_logger.info.assert_any_call("Added 2 missing days to the logbook.")


@pytest.mark.fast
def test_add_missing_days_sunday(logbook: lb.Logbook, relative_precision: float) -> None:
    """Test that add_missing_days_to_logbook adds missing Sunday."""
    # Create a logbook with gap that includes a Sunday
    df = pd.DataFrame(
        {
            "weekday": ["Sat", "Mon"],  # Gap includes Sunday
            "date": ["06.01.2024", "08.01.2024"],  # Sat to Mon (Sun is 07.01.2024)
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": [60, 60],
            "work_time": [8.0, 8.0],
            "case": ["overtime", "overtime"],
            "overtime": [0.0, 0.0],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Missing days: Sat to Mon (should add Sunday)
    missing_days = [(datetime(2024, 1, 6), datetime(2024, 1, 8))]

    with patch("src.logbook.logger") as mock_logger:
        logbook.add_missing_days_to_logbook(missing_days)

        # Verify Sunday was added
        result_df = logbook.load_logbook()
        assert len(result_df) == 3

        # Check that Sunday was added with correct format
        sunday_row = result_df[result_df["date"] == "07.01.2024"].iloc[0]
        assert sunday_row["weekday"] == "Sun"
        assert not sunday_row["start_time"]
        assert not sunday_row["end_time"]
        assert not sunday_row["lunch_break_duration"]
        assert sunday_row["work_time"] == pytest.approx(0.0, rel=relative_precision)
        assert not sunday_row["case"]
        assert not sunday_row["overtime"]

        # Verify logging
        mock_logger.info.assert_called_with("Added 1 missing days to the logbook.")


@pytest.mark.fast
def test_add_missing_days_holiday(logbook: lb.Logbook, relative_precision: float, caplog: pytest.LogCaptureFixture) -> None:
    """Test that add_missing_days_to_logbook adds missing holiday."""
    # Create a logbook with gap that includes a holiday (New Year's Day)
    df = pd.DataFrame(
        {
            "weekday": ["Sun", "Tue"],  # Gap includes New Year's Day (01.01.2024)
            "date": ["31.12.2023", "02.01.2024"],  # Sun to Tue (Mon is 01.01.2024 - New Year's Day)
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": [60, 60],
            "work_time": [8.0, 8.0],
            "case": ["overtime", "overtime"],
            "overtime": [0.0, 0.0],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Missing days: Sun to Tue (should add New Year's Day)
    missing_days = [(datetime(2023, 12, 31), datetime(2024, 1, 2))]

    expected_holiday_name = ["New Year's Day", "Neujahr"]

    with caplog.at_level(logging.INFO):
        logbook.add_missing_days_to_logbook(missing_days)

        # Verify holiday was added
        result_df = logbook.load_logbook()
        assert len(result_df) == 3

        # Check that holiday was added with correct format
        holiday_row = result_df[result_df["date"] == "01.01.2024"].iloc[0]
        print(holiday_row)
        assert holiday_row["weekday"] == "Mon"
        assert holiday_row["start_time"] in expected_holiday_name
        assert not holiday_row["end_time"]
        assert not holiday_row["lunch_break_duration"]
        assert holiday_row["work_time"] == pytest.approx(0.0, rel=relative_precision)
        assert not holiday_row["case"]
        assert not holiday_row["overtime"]

        # Verify logging
        assert "Added missing holiday on 01.01.2024 - " in caplog.text


@pytest.mark.fast
def test_add_missing_days_multiple_days(logbook: lb.Logbook) -> None:
    """Test that add_missing_days_to_logbook adds multiple missing days."""
    # Create a logbook with gap that includes multiple days
    df = pd.DataFrame(
        {
            "weekday": ["Fri", "Wed"],  # Gap includes Sat, Sun, Mon, Tue
            "date": ["05.01.2024", "10.01.2024"],  # Fri to Wed
            "start_time": ["09:00", "09:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": [60, 60],
            "work_time": [8.0, 8.0],
            "case": ["overtime", "overtime"],
            "overtime": [0.0, 0.0],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Gap from Fri to Wed (should add Sat, Sun, Mon, Tue)
    gap_boundaries = [(datetime(2024, 1, 5), datetime(2024, 1, 10))]

    with patch("src.logbook.logger") as mock_logger:
        logbook.add_missing_days_to_logbook(gap_boundaries)

        # Verify that Saturday, Sunday, Monday and Tuesday were added
        result_df = logbook.load_logbook()
        assert len(result_df) == 6

        # Check that Saturday and Sunday were added
        saturday_row = result_df[result_df["date"] == "06.01.2024"].iloc[0]
        sunday_row = result_df[result_df["date"] == "07.01.2024"].iloc[0]
        monday_row = result_df[result_df["date"] == "08.01.2024"].iloc[0]
        tuesday_row = result_df[result_df["date"] == "09.01.2024"].iloc[0]

        assert saturday_row["weekday"] == "Sat"
        assert sunday_row["weekday"] == "Sun"
        assert monday_row["weekday"] == "Mon"
        assert tuesday_row["weekday"] == "Tue"

        # Verify logging calls
        assert mock_logger.info.call_count


@pytest.mark.fast
def test_add_missing_days_already_exists(logbook: lb.Logbook) -> None:
    """Test that add_missing_days_to_logbook skips days that already exist."""
    # Create a logbook with Saturday already present
    df = pd.DataFrame(
        {
            "weekday": ["Fri", "Sat", "Mon"],  # Saturday already exists
            "date": ["05.01.2024", "06.01.2024", "08.01.2024"],
            "start_time": ["09:00", "09:00", "09:00"],
            "end_time": ["17:00", "17:00", "17:00"],
            "lunch_break_duration": [60, 60, 60],
            "work_time": [8.0, 8.0, 8.0],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": [0.0, 0.0, 0.0],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Missing days: Fri to Mon (Saturday already exists)
    missing_days = [(datetime(2024, 1, 5), datetime(2024, 1, 8))]

    with patch("src.logbook.logger") as mock_logger:
        logbook.add_missing_days_to_logbook(missing_days)

        # Verify only Sunday was added (Saturday already exists)
        result_df = logbook.load_logbook()
        assert len(result_df) == 4  # Original 3 existing days (Fri, Sat, Mon) + 1 missing day (Sunday)

        # Verify no logging calls for Saturday (since it already exists)
        saturday_log_calls = [call for call in mock_logger.info.call_args_list if "Saturday" in str(call)]
        assert len(saturday_log_calls) == 0


@pytest.mark.fast
def test_add_missing_days_multiple_ranges(logbook: lb.Logbook) -> None:
    """Test that add_missing_days_to_logbook handles multiple date ranges."""
    # Create a logbook with multiple gaps
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Wed", "Fri"],
            "date": ["01.01.2024", "03.01.2024", "05.01.2024"],
            "start_time": ["09:00", "09:00", "09:00"],
            "end_time": ["17:00", "17:00", "17:00"],
            "lunch_break_duration": [60, 60, 60],
            "work_time": [8.0, 8.0, 8.0],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": [0.0, 0.0, 0.0],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Multiple missing day ranges (Tue and Thu are weekdays, not weekends nor holidays)
    gap_boundaries = [
        (datetime(2024, 1, 1), datetime(2024, 1, 3)),  # Mon to Wed (Tue is weekday)
        (datetime(2024, 1, 3), datetime(2024, 1, 5)),  # Wed to Fri (Thu is weekday)
    ]

    logbook.add_missing_days_to_logbook(gap_boundaries)

    # Verify that Tuesday and Thursday were added
    result_df = logbook.load_logbook()
    assert len(result_df) == 5


@pytest.mark.fast
def test_add_missing_days_sorts_result(logbook: lb.Logbook) -> None:
    """Test that add_missing_days_to_logbook sorts the result by date."""
    # Create a logbook with unsorted dates
    df = pd.DataFrame(
        {
            "weekday": ["Wed", "Mon"],  # Out of order
            "date": ["03.01.2024", "01.01.2024"],
            "start_time": ["09:00", "09:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["8.0", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.0"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Gap from Mon to Wed (should add Tuesday)
    gap_boundaries = [(datetime(2024, 1, 1), datetime(2024, 1, 3))]

    logbook.add_missing_days_to_logbook(gap_boundaries)

    # Verify result is sorted by date and that Tuesday is added
    result_df = logbook.load_logbook()
    expected_dates = ["01.01.2024", "02.01.2024", "03.01.2024"]
    actual_dates = result_df["date"].tolist()
    assert actual_dates == expected_dates


@pytest.mark.fast
def test_add_missing_days_with_mock_load_logbook(logbook: lb.Logbook) -> None:
    """Test that add_missing_days_to_logbook uses load_logbook method correctly."""
    # Mock the load_logbook method to return a specific DataFrame
    mock_df = pd.DataFrame(
        {
            "weekday": ["Mon", "Wed"],
            "date": ["01.01.2024", "03.01.2024"],
            "start_time": ["09:00", "09:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["8.0", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.0"],
        },
    )

    missing_days = [(datetime(2024, 1, 1), datetime(2024, 1, 3))]

    with (
        patch.object(logbook, "load_logbook", return_value=mock_df) as mock_load,
        patch.object(logbook, "save_logbook") as mock_save,
        patch("src.logbook.logger") as mock_logger,
    ):
        logbook.add_missing_days_to_logbook(missing_days)

        # Verify load_logbook was called
        mock_load.assert_called_once()

        # Verify save_logbook was called
        mock_save.assert_called_once()

        # Verify logging happened
        assert mock_logger.info.call_count == 1


@pytest.mark.fast
def test_add_missing_days_edge_case_single_day_gap(logbook: lb.Logbook) -> None:
    """Test that add_missing_days_to_logbook handles single day gaps correctly."""
    # Create a logbook with single day gap
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Wed"],  # Gap of one day (Tue)
            "date": ["01.01.2024", "03.01.2024"],
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["8.0", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.0"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Missing days: Mon to Wed (Tue is weekday, not weekend or holiday)
    missing_days = [(datetime(2024, 1, 1), datetime(2024, 1, 3))]

    logbook.add_missing_days_to_logbook(missing_days)

    # Verify no days were added (Tuesday is weekday)
    result_df = logbook.load_logbook()
    assert len(result_df) == 3


@pytest.mark.fast
def test_add_missing_days_no_weekend_nor_holiday(logbook: lb.Logbook) -> None:
    """Test that add_missing_days_to_logbook does add weekdays that aren't holidays."""
    # Create a logbook with gap that includes only weekdays (no weekends nor holidays)
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Thu"],  # Gap includes Tue, Wed (weekdays)
            "date": ["01.01.2024", "04.01.2024"],  # Mon to Thu
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["8.0", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.0"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    # Missing days: Mon to Thu (Tue, Wed are weekdays, not weekends nor holidays)
    missing_days = [(datetime(2024, 1, 1), datetime(2024, 1, 4))]

    logbook.add_missing_days_to_logbook(missing_days)

    # Verify no days were added (weekdays are not added)
    result_df = logbook.load_logbook()
    assert len(result_df) == 4

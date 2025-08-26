from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

import src.logbook as lb


@pytest.mark.fast
def test_find_missing_days_empty_logbook(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook returns empty list for empty logbook."""
    # Create an empty logbook
    df = logbook.load_logbook()
    assert len(df) == 0
    logbook.save_logbook(df)

    with patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()

        assert result == []
        mock_logger.warning.assert_called_once()
        assert "Log file is empty" in mock_logger.warning.call_args[0][0]


@pytest.mark.fast
def test_find_missing_days_single_entry(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook returns empty list for single entry."""
    # Create a logbook with a single entry
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": ["01.01.2024"],
            "start_time": ["08:00"],
            "end_time": ["17:30"],
            "lunch_break_duration": ["60"],
            "work_time": ["8.0"],
            "case": ["overtime"],
            "overtime": ["0.5"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)
    with patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()
        assert result == []
        mock_logger.warning.assert_not_called()


@pytest.mark.fast
def test_find_missing_days_consecutive_days(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook returns empty list for consecutive days."""
    # Create a logbook with consecutive days
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00", "08:00", "08:00"],
            "end_time": ["17:00", "17:30", "17:00"],
            "lunch_break_duration": ["60", "60", "60"],
            "work_time": ["8.0", "8.0", "8.0"],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": ["0.0", "0.5", "0.0"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)
    with patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()
        assert result == []
        mock_logger.warning.assert_not_called()


@pytest.mark.fast
def test_find_missing_days_single_gap(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook finds a single gap between dates."""
    # Create a logbook with a gap (missing one day)
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Wed"],  # Missing Tuesday
            "date": ["01.01.2024", "03.01.2024"],
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:30"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["8.0", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.5"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    with patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()

        # Should find one gap
        assert len(result) == 1
        start_date, end_date = result[0]
        assert start_date == datetime(2024, 1, 1)
        assert end_date == datetime(2024, 1, 3)

        # Should log a warning
        mock_logger.warning.assert_called_once()
        assert "There are gaps in the logbook between" in mock_logger.warning.call_args[0][0]


@pytest.mark.fast
def test_find_missing_days_multiple_gaps(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook finds multiple gaps between dates."""
    # Create a logbook with multiple gaps
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Wed", "Fri"],  # Missing Tuesday and Thursday
            "date": ["01.01.2024", "03.01.2024", "05.01.2024"],
            "start_time": ["08:00", "08:00", "08:00"],
            "end_time": ["17:15", "17:30", "17:00"],
            "lunch_break_duration": ["60", "60", "60"],
            "work_time": ["8.0", "8.0", "8.0"],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": ["0.25", "0.5", "0.0"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    with patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()

        # Should find two gaps
        assert len(result) == 2

        # First gap: Mon to Wed (missing Tue)
        start_date1, end_date1 = result[0]
        assert start_date1 == datetime(2024, 1, 1)
        assert end_date1 == datetime(2024, 1, 3)

        # Second gap: Wed to Fri (missing Thu)
        start_date2, end_date2 = result[1]
        assert start_date2 == datetime(2024, 1, 3)
        assert end_date2 == datetime(2024, 1, 5)

        # Should log two warnings
        assert mock_logger.warning.call_count == 2


@pytest.mark.fast
def test_find_missing_days_large_gap(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook finds a large gap between dates."""
    # Create a logbook with a large gap (missing several days)
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Fri"],  # Missing Tue, Wed, Thu
            "date": ["01.01.2024", "05.01.2024"],
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:30"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["8.0", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.5"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    with patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()

        # Should find one gap
        assert len(result) == 1
        start_date, end_date = result[0]
        assert start_date == datetime(2024, 1, 1)
        assert end_date == datetime(2024, 1, 5)

        # Should log a warning
        mock_logger.warning.assert_called_once()


@pytest.mark.fast
def test_find_missing_days_unsorted_dates(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook handles unsorted dates correctly."""
    # Create a logbook with unsorted dates
    df = pd.DataFrame(
        {
            "weekday": ["Wed", "Mon", "Fri"],  # Out of order
            "date": ["03.01.2024", "01.01.2024", "05.01.2024"],
            "start_time": ["08:00", "08:00", "08:00"],
            "end_time": ["17:00", "17:00", "17:00"],
            "lunch_break_duration": ["60", "60", "60"],
            "work_time": ["8.0", "8.0", "8.0"],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": ["0.0", "0.5", "0.0"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    with patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()

        # The method processes dates in the order they appear in the DataFrame
        # So it compares: Wed(03.01) -> Mon(01.01) -> Fri(05.01)
        # The gap is from Mon(01.01) to Fri(05.01) (missing Tue, Wed, Thu)
        assert len(result) == 1

        # The gap is from Mon (01.01.2024) to Fri (05.01.2024)
        start_date, end_date = result[0]
        assert start_date == datetime(2024, 1, 1)  # Mon
        assert end_date == datetime(2024, 1, 5)  # Fri

        # Should log one warning
        assert mock_logger.warning.call_count == 1


@pytest.mark.fast
def test_find_missing_days_edge_case_same_day(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook handles same-day entries correctly."""
    # Create a logbook with same-day entries (should not be considered missing)
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon"],  # Same day, different entries
            "date": ["01.01.2024", "01.01.2024"],
            "start_time": ["08:00", "08:00"],
            "end_time": ["12:00", "17:00"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["3.0", "3.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.5"],
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    with patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()
        # Should not find any gaps (same day entries)
        assert result == []
        mock_logger.warning.assert_not_called()


@pytest.mark.fast
def test_find_missing_days_with_mock_load_logbook(logbook: lb.Logbook) -> None:
    """Test that find_missing_days_in_logbook uses load_logbook method correctly."""
    # Mock the load_logbook method to return a specific DataFrame
    mock_df = pd.DataFrame(
        {
            "weekday": ["Mon", "Wed"],
            "date": ["01.01.2024", "03.01.2024"],
            "start_time": ["08:00", "08:00"],
            "end_time": ["17:00", "17:00"],
            "lunch_break_duration": ["60", "60"],
            "work_time": ["8.0", "8.0"],
            "case": ["overtime", "overtime"],
            "overtime": ["0.0", "0.5"],
        },
    )
    with patch.object(logbook, "load_logbook", return_value=mock_df), patch("src.logbook.logger") as mock_logger:
        result = logbook.find_missing_days_in_logbook()
        assert len(result) == 1
        start_date, end_date = result[0]
        assert start_date == datetime(2024, 1, 1)
        assert end_date == datetime(2024, 1, 3)
        mock_logger.warning.assert_called_once()

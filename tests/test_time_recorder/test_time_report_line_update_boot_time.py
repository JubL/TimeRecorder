from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

import psutil
import pytest

import src.time_recorder as tr


@pytest.mark.fast
@patch("psutil.boot_time")
def test_update_boot_time_sets_start_time_to_boot_time(
    mock_boot_time: Mock,
    line: tr.TimeRecorder,
    fake_boot_timestamp: float,
) -> None:
    """Test that update_boot_time sets start_time to the system boot time."""
    mock_boot_time.return_value = fake_boot_timestamp

    old_end_time = line.end_time

    line.update_boot_time()

    assert line.start_time == datetime.fromtimestamp(fake_boot_timestamp, tz=ZoneInfo(line.timezone))
    # End time should have the same date as boot time, but same time as before
    assert line.end_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
    assert line.end_time.time() == old_end_time.time()
    # Work hours and overtime should be recalculated
    assert isinstance(line.work_time, timedelta)
    assert line.case in {"overtime", "undertime"}
    assert isinstance(line.overtime, timedelta)


@pytest.mark.fast
@patch("psutil.boot_time")
def test_update_boot_time_updates_weekday_and_date(mock_boot_time: Mock, line: tr.TimeRecorder, fake_boot_timestamp: float) -> None:
    """Test that update_boot_time updates weekday and date to match the boot time."""
    mock_boot_time.return_value = fake_boot_timestamp

    line.update_boot_time()

    # The start_time and end_time date should match the boot date
    assert line.start_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
    assert line.end_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
    # The weekday should match the boot date's weekday
    expected_weekday = datetime.fromtimestamp(fake_boot_timestamp).strftime("%a")
    assert line.weekday == expected_weekday


@pytest.mark.fast
@patch("psutil.boot_time")
def test_update_boot_time_psutil_error_handling(mock_boot_time: Mock, line: tr.TimeRecorder) -> None:
    """Test that update_boot_time raises BootTimeError when psutil.boot_time fails."""
    # Mock psutil.boot_time to raise a psutil.Error
    mock_boot_time.side_effect = psutil.Error("Access denied")

    # Should raise BootTimeError with appropriate error message
    with pytest.raises(tr.BootTimeError, match="Error accessing system information"):
        line.update_boot_time()


@pytest.mark.fast
@patch("psutil.boot_time")
def test_update_boot_time_value_error_handling(mock_boot_time: Mock, line: tr.TimeRecorder) -> None:
    """Test that update_boot_time raises BootTimeError when datetime parsing fails."""
    # Mock psutil.boot_time to return a valid timestamp
    mock_boot_time.return_value = datetime(2025, 4, 24, 6, 30, 0, tzinfo=ZoneInfo("Europe/Berlin")).timestamp()

    # Modify the line's date_format to be incompatible with the date string
    # This will cause a ValueError when update_boot_time tries to parse the date
    line.date_format = "%Y-%m-%d"  # Change to incompatible format

    # This should cause a ValueError when trying to parse the date with the wrong format
    with pytest.raises(tr.BootTimeError, match="Failed to adjust end time"):
        line.update_boot_time()

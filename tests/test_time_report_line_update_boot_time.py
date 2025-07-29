from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

import time_recorder as tr


@pytest.fixture
def fake_boot_timestamp() -> float:
    """Fixture to provide a fake boot timestamp."""
    return datetime(2025, 4, 25, 6, 30, 0).timestamp()


@pytest.fixture
def sample_line() -> tr.TimeRecorder:
    """Fixture to create a sample TimeRecorder for testing."""
    return tr.TimeRecorder(
        date="24.04.2025",
        start_time="07:32",
        end_time="15:40",
        lunch_break_duration=60,
    )


@pytest.mark.fast
@patch("psutil.boot_time")
def test_update_boot_time_sets_start_time_to_boot_time(
    mock_boot_time: Mock, sample_line: tr.TimeRecorder, fake_boot_timestamp: float
) -> None:
    """Test that update_boot_time sets start_time to the system boot time."""
    mock_boot_time.return_value = fake_boot_timestamp

    old_end_time = sample_line.end_time

    sample_line.update_boot_time()

    assert sample_line.start_time == datetime.fromtimestamp(fake_boot_timestamp)
    # End time should have the same date as boot time, but same time as before
    assert sample_line.end_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
    assert sample_line.end_time.time() == old_end_time.time()
    # Work hours and overtime should be recalculated
    assert isinstance(sample_line.work_time, timedelta)
    assert sample_line.case in {"overtime", "undertime"}
    assert isinstance(sample_line.overtime, timedelta)


@pytest.mark.fast
@patch("psutil.boot_time")
def test_update_boot_time_updates_weekday_and_date(mock_boot_time: Mock, sample_line: tr.TimeRecorder, fake_boot_timestamp: float) -> None:
    """Test that update_boot_time updates weekday and date to match the boot time."""
    mock_boot_time.return_value = fake_boot_timestamp

    sample_line.update_boot_time()

    # The start_time and end_time date should match the boot date
    assert sample_line.start_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
    assert sample_line.end_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
    # The weekday should match the boot date's weekday
    expected_weekday = datetime.fromtimestamp(fake_boot_timestamp).strftime("%a")
    assert sample_line.weekday == expected_weekday

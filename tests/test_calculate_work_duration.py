from datetime import datetime, timedelta

import pytest

import time_recorder as tr


@pytest.fixture
def sample_line() -> tr.TimeRecorder:
    """Fixture to create a sample TimeRecorder for testing."""
    return tr.TimeRecorder(
        date="24.04.2025",
        start_time="08:30",
        end_time="17:30",
        lunch_break_duration=60,
    )


@pytest.mark.fast
def test_standard_duration(sample_line: tr.TimeRecorder) -> None:
    """Tests that the calculate_work_duration method of sample_line returns a timedelta object."""
    duration = sample_line.calculate_work_duration()
    assert isinstance(duration, timedelta)
    assert duration == timedelta(hours=8)


@pytest.mark.fast
def test_no_lunch_break(sample_line: tr.TimeRecorder) -> None:
    """Test that work duration is correct when there is no lunch break."""
    sample_line.lunch_break_duration = timedelta(minutes=0)
    sample_line.start_time = datetime.strptime("24.04.2025 09:00:00", "%d.%m.%Y %H:%M:%S")
    sample_line.end_time = datetime.strptime("24.04.2025 17:00:00", "%d.%m.%Y %H:%M:%S")
    duration = sample_line.calculate_work_duration()
    assert duration == timedelta(hours=8)


@pytest.mark.fast
def test_short_shift(sample_line: tr.TimeRecorder) -> None:
    """Test that a short shift with a lunch break calculates the correct duration."""
    sample_line.start_time = datetime.strptime("24.04.2025 13:15:00", "%d.%m.%Y %H:%M:%S")
    sample_line.end_time = datetime.strptime("24.04.2025 15:45:00", "%d.%m.%Y %H:%M:%S")
    sample_line.lunch_break_duration = timedelta(minutes=15)
    duration = sample_line.calculate_work_duration()
    assert duration == timedelta(hours=2, minutes=15)


@pytest.mark.fast
def test_start_time_after_end_time_raises(sample_line: tr.TimeRecorder) -> None:
    """Test that providing a start time after the end time raises a ValueError."""
    sample_line.start_time = datetime.strptime("24.04.2025 18:00:00", "%d.%m.%Y %H:%M:%S")
    sample_line.end_time = datetime.strptime("24.04.2025 16:00:00", "%d.%m.%Y %H:%M:%S")
    with pytest.raises(ValueError, match="The start time must be before the end time."):
        sample_line.calculate_work_duration()


@pytest.mark.fast
def test_negative_lunch_break_raises(sample_line: tr.TimeRecorder) -> None:
    """Test that a negative lunch break duration raises a ValueError."""
    sample_line.lunch_break_duration = timedelta(minutes=-10)
    with pytest.raises(ValueError, match="The lunch break duration must be a non-negative integer."):
        sample_line.calculate_work_duration()


@pytest.mark.fast
def test_zero_or_negative_work_duration_raises(sample_line: tr.TimeRecorder) -> None:
    """Test that zero or negative work duration raises a ValueError."""
    sample_line.start_time = datetime.strptime("24.04.2025 08:00:00", "%d.%m.%Y %H:%M:%S")
    sample_line.end_time = datetime.strptime("24.04.2025 08:30:00", "%d.%m.%Y %H:%M:%S")
    sample_line.lunch_break_duration = timedelta(minutes=30)
    with pytest.raises(ValueError, match="The work duration must be positive."):
        sample_line.calculate_work_duration()

    sample_line.end_time = datetime.strptime("24.04.2025 08:20:00", "%d.%m.%Y %H:%M:%S")
    sample_line.lunch_break_duration = timedelta(minutes=30)
    with pytest.raises(ValueError, match="The work duration must be positive."):
        sample_line.calculate_work_duration()

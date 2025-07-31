from datetime import datetime, timedelta

import pytest

import src.time_recorder as tr


@pytest.mark.fast
def test_standard_duration(line: tr.TimeRecorder) -> None:
    """Tests that the calculate_work_duration method of sample_line returns a timedelta object."""
    duration = line.calculate_work_duration()
    assert isinstance(duration, timedelta)
    assert duration == timedelta(hours=8)


@pytest.mark.fast
def test_no_lunch_break(line: tr.TimeRecorder) -> None:
    """Test that work duration is correct when there is no lunch break."""
    line.lunch_break_duration = timedelta(minutes=0)
    line.start_time = datetime.strptime("24.04.2025 09:00:00", "%d.%m.%Y %H:%M:%S")
    line.end_time = datetime.strptime("24.04.2025 17:00:00", "%d.%m.%Y %H:%M:%S")
    duration = line.calculate_work_duration()
    assert duration == timedelta(hours=8)


@pytest.mark.fast
def test_short_shift(line: tr.TimeRecorder) -> None:
    """Test that a short shift with a lunch break calculates the correct duration."""
    line.start_time = datetime.strptime("24.04.2025 13:15:00", "%d.%m.%Y %H:%M:%S")
    line.end_time = datetime.strptime("24.04.2025 15:45:00", "%d.%m.%Y %H:%M:%S")
    line.lunch_break_duration = timedelta(minutes=15)
    duration = line.calculate_work_duration()
    assert duration == timedelta(hours=2, minutes=15)


@pytest.mark.fast
def test_start_time_after_end_time_raises(line: tr.TimeRecorder) -> None:
    """Test that providing a start time after the end time raises a ValueError."""
    line.start_time = datetime.strptime("24.04.2025 18:00:00", "%d.%m.%Y %H:%M:%S")
    line.end_time = datetime.strptime("24.04.2025 16:00:00", "%d.%m.%Y %H:%M:%S")
    with pytest.raises(ValueError, match="The start time must be before the end time."):
        line.calculate_work_duration()


@pytest.mark.fast
def test_negative_lunch_break_raises(line: tr.TimeRecorder) -> None:
    """Test that a negative lunch break duration raises a ValueError."""
    line.lunch_break_duration = timedelta(minutes=-10)
    with pytest.raises(ValueError, match="The lunch break duration must be a non-negative integer."):
        line.calculate_work_duration()


@pytest.mark.fast
def test_zero_or_negative_work_duration_raises(line: tr.TimeRecorder) -> None:
    """Test that zero or negative work duration raises a ValueError."""
    line.start_time = datetime.strptime("24.04.2025 08:00:00", "%d.%m.%Y %H:%M:%S")
    line.end_time = datetime.strptime("24.04.2025 08:30:00", "%d.%m.%Y %H:%M:%S")
    line.lunch_break_duration = timedelta(minutes=30)
    with pytest.raises(ValueError, match="The work duration must be positive."):
        line.calculate_work_duration()

    line.end_time = datetime.strptime("24.04.2025 08:20:00", "%d.%m.%Y %H:%M:%S")
    line.lunch_break_duration = timedelta(minutes=30)
    with pytest.raises(ValueError, match="The work duration must be positive."):
        line.calculate_work_duration()

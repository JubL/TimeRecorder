from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

import src.time_recorder as tr


@pytest.mark.parametrize(
    "case",
    [
        {
            "date": "24.04.2025",
            "start_time": "07:32",
            "end_time": "15:40",
            "lunch_break_duration": 60,
            "full_format": "%d.%m.%Y %H:%M:%S",
            "expected_date": "24.04.2025",
            "expected_start": datetime.strptime("24.04.2025 07:32:00", "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin")),
            "expected_end": datetime.strptime("24.04.2025 15:40:00", "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin")),
            "expected_lunch": timedelta(minutes=60),
        },
        {
            "date": "2025-04-24",
            "start_time": "07:32:00",
            "end_time": "15:40:00",
            "lunch_break_duration": 45,
            "full_format": "%Y-%m-%d %H:%M:%S",
            "expected_date": "2025-04-24",
            "expected_start": datetime.strptime("2025-04-24 07:32:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin")),
            "expected_end": datetime.strptime("2025-04-24 15:40:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin")),
            "expected_lunch": timedelta(minutes=45),
        },
    ],
)
@pytest.mark.fast
def test_init_valid(case: dict) -> None:
    """Test valid initialization of TimeRecorder with various formats."""
    line = tr.TimeRecorder(
        date=case["date"],
        start_time=case["start_time"],
        end_time=case["end_time"],
        lunch_break_duration=case["lunch_break_duration"],
        full_format=case["full_format"],
        timezone="Europe/Berlin",
    )
    assert line.date == case["expected_date"]
    assert line.start_time == case["expected_start"]
    assert line.end_time == case["expected_end"]
    assert line.lunch_break_duration == case["expected_lunch"]
    assert isinstance(line.work_time, timedelta)
    assert line.case in {"overtime", "undertime"}
    assert isinstance(line.overtime, timedelta)
    assert isinstance(line.weekday, str)
    assert line.full_format == case["full_format"]
    assert isinstance(line.date_format, str)
    assert isinstance(line.time_format, str)


@pytest.mark.fast
def test_init_missing_seconds_in_time() -> None:
    """Test that missing seconds in time strings are handled by appending ':00'."""
    # Should append ":00" to time strings missing seconds
    line = tr.TimeRecorder(
        date="24.04.2025",
        start_time="08:00",
        end_time="16:00",
        lunch_break_duration=30,
        timezone="Europe/Berlin",
    )
    assert line.start_time == datetime.strptime("24.04.2025 08:00:00", "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin"))
    assert line.end_time == datetime.strptime("24.04.2025 16:00:00", "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin"))


@pytest.mark.fast
def test_init_invalid_time_format_raises() -> None:
    """Test that invalid time format raises a ValueError."""
    with pytest.raises(ValueError, match="time data|does not match format|invalid"):
        tr.TimeRecorder(
            date="24.04.2025",
            start_time="invalid",
            end_time="16:00",
            lunch_break_duration=30,
        )


@pytest.mark.fast
def test_init_start_time_after_end_time_raises() -> None:
    """Test that providing a start time after the end time raises a ValueError."""
    with pytest.raises(ValueError, match="The start time must be before the end time."):
        tr.TimeRecorder(
            date="24.04.2025",
            start_time="18:00",
            end_time="16:00",
            lunch_break_duration=30,
        )


@pytest.mark.fast
def test_init_negative_lunch_break_raises() -> None:
    """Test that a negative lunch break duration raises a ValueError."""
    with pytest.raises(ValueError, match="The lunch break duration must be a non-negative integer."):
        tr.TimeRecorder(
            date="24.04.2025",
            start_time="08:00",
            end_time="16:00",
            lunch_break_duration=-10,
        )


@pytest.mark.fast
def test_init_zero_duration_raises() -> None:
    """Test that a zero work duration raises a ValueError."""
    with pytest.raises(ValueError, match="The work duration must be positive."):
        tr.TimeRecorder(
            date="24.04.2025",
            start_time="08:00",
            end_time="08:01",
            lunch_break_duration=2,
        )

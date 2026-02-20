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
            "end_now": False,
            "lunch_break_duration": 60,
            "full_format": "%d.%m.%Y %H:%M:%S",
            "timezone": "Europe/Berlin",
            "standard_work_hours": 8,
            "expected_date": "24.04.2025",
            "expected_start": datetime.strptime("24.04.2025 07:32:00", "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin")),
            "expected_end": datetime.strptime("24.04.2025 15:40:00", "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin")),
            "expected_lunch": timedelta(minutes=60),
        },
        {
            "date": "2025-04-24",
            "start_time": "07:32:00",
            "end_time": "15:40:00",
            "end_now": False,
            "lunch_break_duration": 45,
            "full_format": "%Y-%m-%d %H:%M:%S",
            "timezone": "Europe/Berlin",
            "standard_work_hours": 8,
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
        {
            "date": case["date"],
            "start_time": case["start_time"],
            "end_time": case["end_time"],
            "end_now": case["end_now"],
            "lunch_break_duration": case["lunch_break_duration"],
            "full_format": case["full_format"],
            "timezone": case["timezone"],
            "standard_work_hours": case["standard_work_hours"],
        },
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
    assert line.standard_work_hours == case["standard_work_hours"]


@pytest.mark.fast
def test_init_missing_seconds_in_time() -> None:
    """Test that missing seconds in time strings are handled by appending ':00'."""
    # Should append ":00" to time strings missing seconds
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:00",
            "end_now": False,
            "lunch_break_duration": 30,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )
    assert line.start_time == datetime.strptime("24.04.2025 08:00:00", "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin"))
    assert line.end_time == datetime.strptime("24.04.2025 16:00:00", "%d.%m.%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin"))


@pytest.mark.fast
def test_init_invalid_time_format_raises() -> None:
    """Test that invalid time format raises a ValueError."""
    with pytest.raises(ValueError, match=r"time data|does not match format|invalid"):
        tr.TimeRecorder(
            {
                "date": "24.04.2025",
                "start_time": "invalid",
                "end_time": "16:00",
                "end_now": False,
                "lunch_break_duration": 30,
                "timezone": "Europe/Berlin",
                "full_format": "%d.%m.%Y %H:%M:%S",
                "standard_work_hours": 8,
            },
        )


@pytest.mark.fast
def test_init_start_time_after_end_time_raises() -> None:
    """Test that providing a start time after the end time raises a ValueError."""
    with pytest.raises(ValueError, match=r"The start time must be before the end time."):
        tr.TimeRecorder(
            {
                "date": "24.04.2025",
                "start_time": "18:00",
                "end_time": "16:00",
                "end_now": False,
                "lunch_break_duration": 30,
                "timezone": "Europe/Berlin",
                "full_format": "%d.%m.%Y %H:%M:%S",
                "standard_work_hours": 8,
            },
        )


@pytest.mark.fast
def test_init_negative_lunch_break_raises() -> None:
    """Test that a negative lunch break duration raises a ValueError."""
    with pytest.raises(ValueError, match=r"The lunch break duration must be a non-negative integer."):
        tr.TimeRecorder(
            {
                "date": "24.04.2025",
                "start_time": "08:00",
                "end_time": "16:00",
                "end_now": False,
                "lunch_break_duration": -10,
                "timezone": "Europe/Berlin",
                "full_format": "%d.%m.%Y %H:%M:%S",
                "standard_work_hours": 8,
            },
        )


@pytest.mark.fast
def test_init_zero_duration_raises() -> None:
    """Test that a zero work duration raises a ValueError."""
    with pytest.raises(ValueError, match=r"The work duration must be positive."):
        tr.TimeRecorder(
            {
                "date": "24.04.2025",
                "start_time": "08:00",
                "end_time": "08:01",
                "end_now": False,
                "lunch_break_duration": 2,
                "timezone": "Europe/Berlin",
                "full_format": "%d.%m.%Y %H:%M:%S",
                "standard_work_hours": 8,
            },
        )


@pytest.mark.fast
def test_init_end_now_sets_end_time_to_current_plus_one_minute() -> None:
    r"""Test that when end_now is True, end_time is set to current time + 1 minute (line 173 in src\time_recorder.py)."""
    # Record time before creating TimeRecorder
    timezone = "Europe/Berlin"
    config_date = "24.04.2025"
    before_time = datetime.now(tz=ZoneInfo(timezone))

    # Create TimeRecorder with end_now=True
    # Note: end_time is provided but will be overwritten by line 173
    line = tr.TimeRecorder(
        {
            "date": config_date,
            "start_time": "08:00",
            "end_time": "16:00",  # This will be overwritten by line 173
            "end_now": True,  # This triggers line 173
            "lunch_break_duration": 0,
            "timezone": timezone,
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    # Line 173 sets data["end_time"] to current time + 1 minute (as time string)
    # Line 174 then parses it using _parse_datetime which combines config_date with the time string
    # So end_time will be: config_date + (current_time + 1 minute)
    expected_date = datetime.strptime(config_date, "%d.%m.%Y").date()

    # Verify end_time uses the config date (not current date)
    assert line.end_time.date() == expected_date
    # Verify timezone is correct
    assert line.end_time.tzinfo == ZoneInfo(timezone)
    # Verify end_time is after start_time
    assert line.end_time > line.start_time

    # Verify the time component is approximately current time + 1 minute
    # Calculate time difference in seconds (ignoring date)
    current_time_seconds = before_time.hour * 3600 + before_time.minute * 60 + before_time.second
    end_time_seconds = line.end_time.hour * 3600 + line.end_time.minute * 60 + line.end_time.second
    time_diff = end_time_seconds - current_time_seconds

    # Allow tolerance of 2 seconds for execution time
    # Time diff should be approximately 60 seconds (1 minute), but account for wrapping
    assert 58 <= time_diff <= 62 or time_diff >= 86398  # 60 ± 2 seconds, or wrapped around midnight

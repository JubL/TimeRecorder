"""Unit tests for the TimeRecorder __repr__ method."""

import pytest

import src.time_recorder as tr


@pytest.mark.fast
def test_repr_basic_format() -> None:
    """Test __repr__ method returns semicolon-separated format."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "17:00",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    # Should have 9 parts (8 semicolons)
    assert len(parts) == 9

    # Check that all expected fields are present
    assert parts[0] == "Thu"  # weekday
    assert parts[1] == "24.04.2025"  # date
    assert parts[2] == "08:00:00"  # start_time
    assert parts[3] == "17:00:00"  # end_time
    assert parts[4] == "60"  # lunch_break_duration
    assert parts[5] == "8.0"  # work_time
    assert parts[6] == "overtime"  # case
    assert parts[7] == "0.0"  # overtime
    assert parts[8] == "Europe/Berlin"  # timezone


@pytest.mark.fast
def test_repr_overtime_case() -> None:
    """Test __repr__ method with overtime case."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00:00",
            "end_time": "17:30:00",  # 9.5 hours total, 1 hour lunch = 8.5 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[0] == "Thu"  # weekday
    assert parts[1] == "24.04.2025"  # date
    assert parts[2] == "08:00:00"  # start_time
    assert parts[3] == "17:30:00"  # end_time
    assert parts[4] == "60"  # lunch_break_duration
    assert parts[5] == "8.5"  # work_time
    assert parts[6] == "overtime"  # case
    assert parts[7] == "0.5"  # overtime
    assert parts[8] == "Europe/Berlin"  # timezone


@pytest.mark.fast
def test_repr_undertime_case() -> None:
    """Test __repr__ method with undertime case."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00:00",
            "end_time": "16:00:00",  # 8 hours total, 1 hour lunch = 7 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[0] == "Thu"  # weekday
    assert parts[1] == "24.04.2025"  # date
    assert parts[2] == "08:00:00"  # start_time
    assert parts[3] == "16:00:00"  # end_time
    assert parts[4] == "60"  # lunch_break_duration
    assert parts[5] == "7.0"  # work_time
    assert parts[6] == "undertime"  # case
    assert parts[7] == "-1.0"  # overtime (negative)
    assert parts[8] == "Europe/Berlin"  # timezone


@pytest.mark.fast
def test_repr_zero_lunch_break() -> None:
    """Test __repr__ method with zero lunch break."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:00",
            "end_now": False,
            "lunch_break_duration": 0,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[4] == "0"  # lunch_break_duration
    assert parts[5] == "8.0"  # work_time (8 hours without lunch break)
    assert parts[6] == "overtime"  # case
    assert parts[7] == "0.0"  # overtime


@pytest.mark.fast
def test_repr_fractional_work_time() -> None:
    """Test __repr__ method with fractional work time."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:30",  # 8.5 hours total, 1 hour lunch = 7.5 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[5] == "7.5"  # work_time
    assert parts[6] == "undertime"  # case
    assert parts[7] == "-0.5"  # overtime (negative)


@pytest.mark.fast
def test_repr_different_timezone() -> None:
    """Test __repr__ method with different timezone."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "17:00",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "America/New_York",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[8] == "America/New_York"  # timezone


@pytest.mark.fast
def test_repr_different_date() -> None:
    """Test __repr__ method with different date."""
    line = tr.TimeRecorder(
        {
            "date": "15.03.2025",
            "start_time": "08:00",
            "end_time": "17:00",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[0] == "Sat"  # weekday (March 15, 2025 is a Saturday)
    assert parts[1] == "15.03.2025"  # date


@pytest.mark.fast
def test_repr_large_overtime() -> None:
    """Test __repr__ method with large overtime."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "19:00",  # 11 hours total, 1 hour lunch = 10 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[5] == "10.0"  # work_time
    assert parts[6] == "overtime"  # case
    assert parts[7] == "2.0"  # overtime


@pytest.mark.fast
def test_repr_large_undertime() -> None:
    """Test __repr__ method with large undertime."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "11:00",  # 3 hours total, 1 hour lunch = 2 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[5] == "2.0"  # work_time
    assert parts[6] == "undertime"  # case
    assert parts[7] == "-6.0"  # overtime (negative)


@pytest.mark.fast
def test_repr_complex_minutes() -> None:
    """Test __repr__ method with complex minute calculations."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:23",  # 8 hours 23 minutes total, 1 hour lunch = 7 hours 23 minutes work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )

    result = repr(line)
    parts = result.split(";")

    assert parts[5] == "7.38"  # work_time (rounded to 2 decimal places)
    assert parts[6] == "undertime"  # case
    assert parts[7] == "-0.62"  # overtime (negative)


@pytest.mark.fast
@pytest.mark.parametrize(
    ("test_data", "expected_parts"),
    [
        (
            {
                "date": "24.04.2025",
                "start_time": "08:00",
                "end_time": "17:00",
                "end_now": False,
                "lunch_break_duration": 60,
                "timezone": "Europe/Berlin",
                "full_format": "%d.%m.%Y %H:%M:%S",
                "standard_work_hours": 8,
            },
            9,
        ),
        (
            {
                "date": "15.03.2025",
                "start_time": "09:00",
                "end_time": "18:00",
                "end_now": False,
                "lunch_break_duration": 30,
                "timezone": "America/New_York",
                "full_format": "%d.%m.%Y %H:%M:%S",
                "standard_work_hours": 8,
            },
            9,
        ),
        (
            {
                "date": "01.01.2025",
                "start_time": "07:30",
                "end_time": "16:45",
                "end_now": False,
                "lunch_break_duration": 45,
                "timezone": "Asia/Tokyo",
                "full_format": "%d.%m.%Y %H:%M:%S",
                "standard_work_hours": 8,
            },
            9,
        ),
    ],
)
def test_repr_format_consistency(test_data: dict, expected_parts: int) -> None:
    """Test that __repr__ format is consistent across different scenarios."""
    line = tr.TimeRecorder(test_data)
    result = repr(line)
    parts = result.split(";")

    # Should always have the same number of parts
    assert len(parts) == expected_parts

    # Should have all required fields
    assert len(parts) >= 8  # At least 8 non-empty parts
    assert parts[0]  # weekday
    assert parts[1]  # date
    assert parts[2]  # start_time
    assert parts[3]  # end_time
    assert parts[4]  # lunch_break_duration
    assert parts[5]  # work_time
    assert parts[6]  # case
    assert parts[7]  # overtime
    assert parts[8]  # timezone

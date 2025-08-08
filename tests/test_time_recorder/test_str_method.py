"""Unit tests for the TimeRecorder __str__ method."""

import pytest

import src.time_recorder as tr


@pytest.mark.fast
def test_str_overtime_case() -> None:
    """Test __str__ method with overtime case."""
    # Create a TimeRecorder with overtime (8.5 hours work time)
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "17:30",  # 9.5 hours total, 1 hour lunch = 8.5 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)

    assert "Total work duration: 8 hours and 30 minutes (8.5)." in result
    assert "Total overtime: 0 hours and 30 minutes." in result
    assert "overtime" in result
    assert "Decimal representation of" in result
    assert "overtime" in result
    assert "is 0.5." in result


@pytest.mark.fast
def test_str_undertime_case() -> None:
    """Test __str__ method with undertime case."""
    # Create a TimeRecorder with undertime (7.5 hours work time)
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:30",  # 8.5 hours total, 1 hour lunch = 7.5 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)

    assert "Total work duration: 7 hours and 30 minutes (7.5)." in result
    assert "Total undertime: -1 hours and 30 minutes." in result
    assert "undertime" in result
    assert "Decimal representation of" in result
    assert "undertime" in result
    assert "is -0.5." in result


@pytest.mark.fast
def test_str_exact_8_hours() -> None:
    """Test __str__ method with exactly 8 hours work time (borderline case)."""
    # Create a TimeRecorder with exactly 8 hours work time
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "17:00",  # 9 hours total, 1 hour lunch = 8 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)

    assert "Total work duration: 8 hours and 0 minutes (8.0)." in result
    assert "Total overtime: 0 hours and 0 minutes." in result
    assert "overtime" in result
    assert "Decimal representation of" in result
    assert "overtime" in result
    assert "is 0.0." in result


@pytest.mark.fast
def test_str_negative_overtime() -> None:
    """Test __str__ method with negative overtime (undertime)."""
    # Create a TimeRecorder with significant undertime (6 hours work time)
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "15:00",  # 7 hours total, 1 hour lunch = 6 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)

    assert "Total work duration: 6 hours and 0 minutes (6.0)." in result
    assert "Total undertime: -2 hours and 0 minutes." in result
    assert "undertime" in result
    assert "Decimal representation of" in result
    assert "undertime" in result
    assert "is -2.0." in result


@pytest.mark.fast
def test_str_large_overtime() -> None:
    """Test __str__ method with large overtime."""
    # Create a TimeRecorder with large overtime (10 hours work time)
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "19:00",  # 11 hours total, 1 hour lunch = 10 hours work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)

    assert "Total work duration: 10 hours and 0 minutes (10.0)." in result
    assert "Total overtime: 2 hours and 0 minutes." in result
    assert "overtime" in result
    assert "Decimal representation of" in result
    assert "overtime" in result
    assert "is 2.0." in result


@pytest.mark.fast
def test_str_partial_hours_and_minutes() -> None:
    """Test __str__ method with partial hours and minutes."""
    # Create a TimeRecorder with complex time (7 hours 45 minutes work time)
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:45",  # 8 hours 45 minutes total, 1 hour lunch = 7 hours 45 minutes work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)

    assert "Total work duration: 7 hours and 45 minutes (7.75)." in result
    assert "Total undertime: -1 hours and 45 minutes." in result
    assert "undertime" in result
    assert "Decimal representation of" in result
    assert "undertime" in result
    assert "is -0.25." in result


@pytest.mark.fast
def test_str_invalid_case_raises_value_error() -> None:
    """Test that __str__ raises ValueError for invalid case values."""
    # Create a TimeRecorder and manually set an invalid case
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:00",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    # Manually set an invalid case
    line.case = "invalid_case"

    with pytest.raises(ValueError, match="Unexpected value for case: invalid_case"):
        str(line)


@pytest.mark.fast
def test_str_empty_case_raises_value_error() -> None:
    """Test that __str__ raises ValueError for empty case value."""
    # Create a TimeRecorder and manually set an empty case
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:00",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    # Manually set an empty case
    line.case = ""

    with pytest.raises(ValueError, match=r"Unexpected value for case: . Expected 'overtime' or 'undertime'."):
        str(line)


@pytest.mark.fast
def test_str_none_case_raises_value_error() -> None:
    """Test that __str__ raises ValueError for None case value."""
    # Create a TimeRecorder and manually set None case
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:00",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    # Manually set None case
    line.case = "None"

    with pytest.raises(ValueError, match="Unexpected value for case: None"):
        str(line)


@pytest.mark.fast
def test_str_format_structure() -> None:
    """Test that __str__ returns the expected format structure."""
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:30",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)
    lines = result.split("\n")

    # Should have exactly 3 lines
    assert len(lines) == 3

    # First line should contain work duration
    assert "Total work duration:" in lines[0]
    assert "hours and" in lines[0]
    assert "minutes" in lines[0]
    assert "(" in lines[0]
    assert ")" in lines[0]

    # Second line should contain overtime/undertime
    assert "Total" in lines[1]
    assert "hours and" in lines[1]
    assert "minutes" in lines[1]

    # Third line should contain decimal representation
    assert "Decimal representation of" in lines[2]
    assert "is" in lines[2]


@pytest.mark.fast
def test_str_decimal_precision() -> None:
    """Test that __str__ shows correct decimal precision."""
    # Create a TimeRecorder with fractional hours
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:20",  # 8 hours 20 minutes total, 1 hour lunch = 7 hours 20 minutes work
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)

    # Should show 7.33 hours (7 hours 20 minutes = 7.33 hours)
    assert "Total work duration: 7 hours and 20 minutes (7.33)." in result
    # Should show -0.67 hours undertime (with ANSI codes)
    assert "Decimal representation of" in result
    assert "undertime" in result
    assert "is -0.67." in result


@pytest.mark.fast
def test_str_minimal_work_time() -> None:
    """Test __str__ method with minimal work time."""
    # Create a TimeRecorder with minimal work time (1 minute work)
    line = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "08:01",  # 1 minute work
            "end_now": False,
            "lunch_break_duration": 0,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result = str(line)

    assert "Total work duration: 0 hours and 1 minutes (0.02)." in result
    assert "Total undertime: -8 hours and 1 minutes." in result
    assert "undertime" in result
    assert "Decimal representation of" in result
    assert "undertime" in result
    assert "is -7.98." in result


@pytest.mark.fast
def test_str_ansi_color_codes_present() -> None:
    """Test that __str__ includes ANSI color codes for overtime/undertime."""
    # First test the overtime case
    line_overtime = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "17:30",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result_overtime = str(line_overtime)

    # Should contain ANSI color codes for overtime (green)
    assert "\x1b[32m" in result_overtime  # Green color code
    assert "\x1b[0m" in result_overtime  # Reset color code

    # Then test the undertime case
    line_undertime = tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:30",
            "end_now": False,
            "lunch_break_duration": 60,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    )

    result_undertime = str(line_undertime)

    # Should contain ANSI color codes for undertime (red)
    assert "\x1b[31m" in result_undertime  # Red color code
    assert "\x1b[0m" in result_undertime  # Reset color code

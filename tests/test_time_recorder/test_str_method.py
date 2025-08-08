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

    assert "Time Recorder - Work Hours calculator" in result
    assert "📅 Date:" in result
    assert "⏰ Start time: 08:00" in result
    assert "⏰ End time: 17:30" in result
    assert "🍽️  Lunch break: 60m" in result
    assert "⏱️  Work duration: 8h and 30m (8.5h)" in result
    assert "📈 Status:" in result
    assert "overtime" in result
    assert "0h and 30m (0.5h)" in result


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

    assert "Time Recorder - Work Hours calculator" in result
    assert "📅 Date:" in result
    assert "⏰ Start time: 08:00" in result
    assert "⏰ End time: 16:30" in result
    assert "🍽️  Lunch break: 60m" in result
    assert "⏱️  Work duration: 7h and 30m (7.5h)" in result
    assert "📈 Status:" in result
    assert "undertime" in result
    assert "-1h and 30m (-0.5h)" in result


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

    assert "Time Recorder - Work Hours calculator" in result
    assert "📅 Date:" in result
    assert "⏰ Start time: 08:00" in result
    assert "⏰ End time: 17:00" in result
    assert "🍽️  Lunch break: 60m" in result
    assert "⏱️  Work duration: 8h and 0m (8.0h)" in result
    assert "📈 Status:" in result
    assert "overtime" in result
    assert "0h and 0m (0.0h)" in result


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

    assert "Time Recorder - Work Hours calculator" in result
    assert "📅 Date:" in result
    assert "⏰ Start time: 08:00" in result
    assert "⏰ End time: 15:00" in result
    assert "🍽️  Lunch break: 60m" in result
    assert "⏱️  Work duration: 6h and 0m (6.0h)" in result
    assert "📈 Status:" in result
    assert "undertime" in result
    assert "-2h and 0m (-2.0h)" in result


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

    assert "Time Recorder - Work Hours calculator" in result
    assert "📅 Date:" in result
    assert "⏰ Start time: 08:00" in result
    assert "⏰ End time: 19:00" in result
    assert "🍽️  Lunch break: 60m" in result
    assert "⏱️  Work duration: 10h and 0m (10.0h)" in result
    assert "📈 Status:" in result
    assert "overtime" in result
    assert "2h and 0m (2.0h)" in result


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

    assert "Time Recorder - Work Hours calculator" in result
    assert "📅 Date:" in result
    assert "⏰ Start time: 08:00" in result
    assert "⏰ End time: 16:45" in result
    assert "🍽️  Lunch break: 60m" in result
    assert "⏱️  Work duration: 7h and 45m (7.75h)" in result
    assert "📈 Status:" in result
    assert "undertime" in result
    assert "-1h and 45m (-0.25h)" in result


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

    # Should have exactly 10 lines (empty, title, separator, empty, date, start, end, lunch, work duration, status)
    assert len(lines) == 10

    # First line should be empty
    assert lines[0] == ""

    # Second line should contain title
    assert "Time Recorder - Work Hours calculator" in lines[1]

    # Third line should contain separator
    assert "=====================================" in lines[2]

    # Fourth line should be empty
    assert lines[3] == ""

    # Fifth line should contain date
    assert "📅 Date:" in lines[4]

    # Sixth line should contain start time
    assert "⏰ Start time:" in lines[5]

    # Seventh line should contain end time
    assert "⏰ End time:" in lines[6]

    # Eighth line should contain lunch break
    assert "🍽️  Lunch break:" in lines[7]

    # Ninth line should contain work duration
    assert "⏱️  Work duration:" in lines[8]

    # Tenth line should contain status
    assert "📈 Status:" in lines[9]


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
    assert "⏱️  Work duration: 7h and 20m (7.33h)" in result
    # Should show -0.67 hours undertime
    assert "📈 Status:" in result
    assert "undertime" in result
    assert "-1h and 20m (-0.67h)" in result


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

    assert "⏱️  Work duration: 0h and 1m (0.02h)" in result
    assert "📈 Status:" in result
    assert "undertime" in result
    assert "-8h and 1m (-7.98h)" in result


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

"""Unit tests for the time_recording module, including TimeRecorder and related functionality."""

import pytest

import src.time_recorder as tr


@pytest.mark.parametrize(
    ("line", "expected_result"),
    [
        (
            tr.TimeRecorder(
                {
                    "date": "24.02.2025",
                    "start_time": "08:00",
                    "end_time": "18:00",
                    "end_now": False,
                    "lunch_break_duration": 30,
                    "timezone": "Europe/Berlin",
                    "full_format": "%d.%m.%Y %H:%M:%S",
                    "standard_work_hours": 8,
                },
            ),
            {
                "weekday": "Mon",  # 24.02.2025 is a Monday
                "date": "24.02.2025",
                "start_time": "08:00:00 CET",
                "end_time": "18:00:00 CET",
                "lunch_break_duration": 30,
                "timezone": "Europe/Berlin",
            },
        ),
        (
            tr.TimeRecorder(
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
            ),
            {
                "weekday": "Thu",  # 24.04.2025 is a Thursday
                "date": "24.04.2025",
                "start_time": "08:00:00 CEST",
                "end_time": "16:00:00 CEST",
                "lunch_break_duration": 30,
                "timezone": "Europe/Berlin",
            },
        ),
        (
            tr.TimeRecorder(
                {
                    "date": "29.07.2025",
                    "start_time": "07:00",
                    "end_time": "17:20",
                    "end_now": False,
                    "lunch_break_duration": 60,
                    "timezone": "Europe/Berlin",
                    "full_format": "%d.%m.%Y %H:%M:%S",
                    "standard_work_hours": 8,
                },
            ),
            {
                "weekday": "Tue",
                "date": "29.07.2025",
                "start_time": "07:00:00 CEST",
                "end_time": "17:20:00 CEST",
                "lunch_break_duration": 60,
                "timezone": "Europe/Berlin",
            },
        ),
    ],
)
@pytest.mark.fast
def test_time_report_line_to_dict_returns_expected_dict(line: tr.TimeRecorder, expected_result: dict) -> None:
    """Test that time_report_line_to_dict returns a dictionary with expected keys and values."""
    result = line.time_report_line_to_dict()
    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "weekday",
        "date",
        "start_time",
        "end_time",
        "lunch_break_duration",
        "work_time",
        "case",
        "overtime",
        "timezone",
    }
    for key, value in expected_result.items():
        assert result[key] == value
    assert isinstance(result["work_time"], float)
    assert result["case"] in {"overtime", "undertime"}
    assert isinstance(result["overtime"], float)

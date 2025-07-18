"""Unit tests for the time_recording module, including TimeRecorder and related functionality."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adjust path to import time_recording module

import time_recorder as tr


class TestTimeRecorderToDict:
    """Tests for TimeRecorder.time_report_line_to_dict."""

    @pytest.fixture
    def line(self) -> tr.TimeRecorder:
        """Fixture to create a sample TimeRecorder for time_report_line_to_dict tests."""
        return tr.TimeRecorder(
            date="24.04.2025",
            start_time="08:00",
            end_time="16:00",
            lunch_break_duration=30,
        )

    @pytest.mark.fast
    def test_time_report_line_to_dict_returns_expected_dict(self, line: tr.TimeRecorder) -> None:
        """Test that time_report_line_to_dict returns a dictionary with expected keys and values."""
        result = line.time_report_line_to_dict()
        results = {
            "weekday": "Thu",  # 24.04.2025 is a Thursday
            "date": "24.04.2025",
            "start_time": "08:00:00",
            "end_time": "16:00:00",
            "lunch_break_duration": 30,
        }
        assert isinstance(result, dict)
        assert set(result.keys()) == {"weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"}
        for key, value in results.items():
            assert result[key] == value
        assert isinstance(result["work_time"], float)
        assert result["case"] in ("overtime", "undertime")
        assert isinstance(result["overtime"], float)

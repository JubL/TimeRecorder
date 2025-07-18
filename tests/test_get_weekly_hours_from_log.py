"""Unit tests for the time_recording module, including TimeRecorder and related functionality."""

import os
import pathlib
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adjust path to import time_recording module

import time_recorder as tr


class TestGetWeeklyHoursFromLog:
    """Tests for TimeRecorder.get_weekly_hours_from_log."""

    @pytest.fixture
    def line(self) -> tr.TimeRecorder:
        """Fixture to create a sample TimeRecorder for get_weekly_hours_from_log tests."""
        return tr.TimeRecorder(
            date="24.04.2025",
            start_time="08:00",
            end_time="16:00",
            lunch_break_duration=30,
        )

    @pytest.mark.fast
    def test_returns_zero_if_file_not_found(self, line: tr.TimeRecorder, tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
        """Should return 0.0 and log error if file does not exist."""
        missing_file = tmp_path / "missing.csv"
        with caplog.at_level("ERROR"):
            result = line.get_weekly_hours_from_log(str(missing_file))
            assert result == 0.0
            assert "Log file not found" in caplog.text

    @pytest.mark.fast
    def test_returns_zero_if_file_empty(self, line: tr.TimeRecorder, tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
        """Should return 0.0 and log warning if file is empty."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        with caplog.at_level("WARNING"):
            result = line.get_weekly_hours_from_log(str(empty_file))
            assert result == 0.0
            assert "Log file is empty" in caplog.text

    @pytest.mark.fast
    def test_returns_zero_if_parser_error(self, line: tr.TimeRecorder, tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
        """Should return 0.0 and log error if file cannot be parsed."""
        bad_file = tmp_path / "bad.csv"
        bad_file.write_text('not;a;"csv')
        with caplog.at_level("ERROR"):
            result = line.get_weekly_hours_from_log(str(bad_file))
            assert result == 0.0
            assert "Error parsing log file" in caplog.text

    @pytest.mark.fast
    def test_returns_zero_if_missing_columns(self, line: tr.TimeRecorder, tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
        """Should return 0.0 and log error if required columns are missing."""
        df = pd.DataFrame({"foo": [1], "bar": [2]})
        file = tmp_path / "missing_cols.csv"
        df.to_csv(file, sep=";", index=False, encoding="utf-8")
        with caplog.at_level("ERROR"):
            result = line.get_weekly_hours_from_log(str(file))
            assert result == 0.0
            assert "must contain 'work_time' and 'date' columns" in caplog.text

    @pytest.mark.fast
    def test_returns_zero_if_no_work_days(self, line: tr.TimeRecorder, tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
        """Should return 0.0 and log warning if no work days are found (all work_time zero)."""
        df = pd.DataFrame({
            "date": ["2025-04-21", "2025-04-22"],
            "work_time": [0, 0]
        })
        file = tmp_path / "no_work.csv"
        df.to_csv(file, sep=";", index=False, encoding="utf-8")
        with caplog.at_level("WARNING"):
            result = line.get_weekly_hours_from_log(str(file))
            assert result == 0.
            assert "No work days found" in caplog.text

    @pytest.mark.fast
    def test_returns_expected_weekly_hours(self, line: tr.TimeRecorder, tmp_path: pytest.LogCaptureFixture) -> None:
        """Should return correct weekly hours for valid log file."""
        df = pd.DataFrame({
            "date": ["2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24", "2025-04-25"],
            "work_time": [8, 7.5, 8, 8.5, 8]  # hours
        })
        file = tmp_path / "log.csv"
        df.to_csv(file, sep=";", index=False, encoding="utf-8")
        # Average per day = (8+7.5+8+8.5+8)/5 = 8.0, so weekly = 8.0*5 = 40.0
        result = line.get_weekly_hours_from_log(str(file))
        assert result == 40.

    @pytest.mark.fast
    def test_ignores_zero_work_time_days(self, line: tr.TimeRecorder, tmp_path: pathlib.Path) -> None:
        """Should only average over days with work_time > 0."""
        df = pd.DataFrame({
            "date": ["2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24", "2025-04-25"],
            "work_time": [8, 0, 8, 0, 8]  # Only 3 days with work
        })
        file = tmp_path / "log2.csv"
        df.to_csv(file, sep=";", index=False, encoding="utf-8")
        # Average per day = (8+8+8)/3 = 8.0, weekly = 8.0*5 = 40.0
        result = line.get_weekly_hours_from_log(str(file))
        assert result == 40.0

    @pytest.mark.fast
    def test_handles_non_numeric_work_time(self, line: tr.TimeRecorder, tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
        """Should log error and return 0.0 if work_time cannot be converted."""
        df = pd.DataFrame({
            "date": ["2025-04-21"],
            "work_time": ["not_a_number"]
        })
        file = tmp_path / "bad_work_time.csv"
        df.to_csv(file, sep=";", index=False, encoding="utf-8")
        with caplog.at_level("ERROR"):
            result = line.get_weekly_hours_from_log(str(file))
            assert result == 0.0
            assert "Error converting 'work_time' to timedelta" in caplog.text

    @pytest.mark.fast
    def test_rounds_to_two_decimals(self, line: tr.TimeRecorder, tmp_path: pathlib.Path) -> None:
        """Should round the result to two decimal places."""
        df = pd.DataFrame({
            "date": ["2025-04-21", "2025-04-22"],
            "work_time": [7.3333, 7.6666]
        })
        file = tmp_path / "round.csv"
        df.to_csv(file, sep=";", index=False, encoding="utf-8")
        # Average = (7.3333+7.6666)/2 = 7.5, weekly = 7.5*5 = 37.5
        result = line.get_weekly_hours_from_log(str(file))
        assert result == 37.5



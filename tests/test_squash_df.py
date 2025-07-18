"""Unit tests for the time_recording module, including TimeRecorder and related functionality."""

import os
import pathlib
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adjust path to import time_recording module

import time_recorder as tr


class TestSquashDF:
    """Tests for TimeRecorder.squash_df."""

    @pytest.fixture
    def line(self) -> tr.TimeRecorder:
        """Fixture to create a sample TimeRecorder for squash_df tests."""
        return tr.TimeRecorder(
            date="24.04.2025",
            start_time="08:00",
            end_time="17:30",
            lunch_break_duration=60,
        )

    @pytest.mark.fast
    def test_squash_df_groups_and_sums_correctly(self, tmp_path: pathlib.Path, line: tr.TimeRecorder) -> None:
        """Test that squash_df groups by date and sums work_time and lunch_break_duration."""
        df_file = tmp_path / "logbook_df.csv"
        # Create a DataFrame with duplicate dates and different work_time/lunch_break_duration
        df = pd.DataFrame({
            "weekday": ["Thu", "Thu", "Fri"],
            "date": ["24.04.2025", "24.04.2025", "25.04.2025"],
            "start_time": ["08:00:00", "11:30:00", "08:00:00"],
            "end_time": ["9:00:00", "17:00:00", "16:00:00"],
            "lunch_break_duration": [1, 60, 60],
            "work_time": [1.0, 6.0, 8.0],
            "case": ["undertime", "undertime", "overtime"],
            "overtime": [-7, 4.5, 0.0],
        })
        df.to_csv(df_file, sep=';', index=False, encoding='utf-8')
        line.squash_df(df_file)
        result = pd.read_csv(df_file, sep=';', encoding='utf-8')
        # Should have two rows (grouped by date and weekday)
        assert len(result) == 2
        # Check that lunch_break_duration and work_time are summed for the grouped date
        grouped = result[result["date"] == "24.04.2025"]
        assert not grouped.empty, "No rows found for date '24.04.2025'"
        assert grouped.iloc[0]["lunch_break_duration"] == 61  # 1 + 60
        assert grouped.iloc[0]["work_time"] == 7  # 1.0 + 6.0
        # Check that start_time is 'first' and end_time is 'last'
        assert grouped.iloc[0]["start_time"] == "08:00:00"
        assert grouped.iloc[0]["end_time"] == "17:00:00"

    @pytest.mark.fast
    def test_squash_df_file_not_found_logs_error(self, tmp_path: pathlib.Path, line: tr.TimeRecorder, caplog: pytest.LogCaptureFixture) -> None:
        """Test that squash_df logs error if file does not exist."""
        missing_file = tmp_path / "missing.csv"
        with caplog.at_level("ERROR"):
            line.squash_df(missing_file)
            assert "File not found" in caplog.text

    @pytest.mark.fast
    def test_squash_df_empty_file_logs_warning(self, tmp_path: pathlib.Path, line: tr.TimeRecorder, caplog: pytest.LogCaptureFixture) -> None:
        """Test that squash_df logs warning if file is empty."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        with caplog.at_level("WARNING"):
            line.squash_df(empty_file)
            assert "DataFrame file is empty" in caplog.text

    @pytest.mark.fast
    def test_squash_df_io_error_logs_error(
            self,
            tmp_path: pathlib.Path,
            line: tr.TimeRecorder,
            caplog: pytest.LogCaptureFixture,
            monkeypatch: pytest.MonkeyPatch
        ) -> None:
        """Test that squash_df logs error on I/O error."""
        df_file = tmp_path / "logbook_df.csv"
        df = pd.DataFrame({
            "weekday": ["Thu"],
            "date": ["24.04.2025"],
            "start_time": ["08:00:00"],
            "end_time": ["16:00:00"],
            "lunch_break_duration": [30],
            "work_time": [8.0],
            "case": ["overtime"],
            "overtime": [0.0],
        })
        df.to_csv(df_file, sep=';', index=False, encoding='utf-8')

        # Simulate OSError when writing to CSV
        def raise_oserror(*_args: list, **_kwargs: dict) -> None:
            raise OSError("Simulated I/O error")

        monkeypatch.setattr(pd.DataFrame, "to_csv", raise_oserror)
        with caplog.at_level("ERROR"):
            line.squash_df(df_file)
            assert "I/O error while squashing DataFrame" in caplog.text

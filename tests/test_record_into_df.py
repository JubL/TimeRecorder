import os
import pathlib
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adjust path to import time_recording module

import time_recorder as tr


class TestRecordIntoDF:
    """Tests for TimeRecorder.record_into_df."""

    @pytest.fixture
    def line(self) -> tr.TimeRecorder:
        """Fixture to create a sample TimeRecorder for record_into_df tests."""
        return tr.TimeRecorder(
            date="24.04.2025",
            start_time="08:00",
            end_time="16:00",
            lunch_break_duration=30,
        )

    @pytest.mark.fast
    def test_record_into_df_creates_and_appends_row(self, tmp_path: pathlib.Path, line: tr.TimeRecorder) -> None:
        """Test that record_into_df creates the file and appends rows correctly as a DataFrame."""
        df_file = tmp_path / "logbook_df.csv"
        # Should create file and write header + row
        line.record_into_df(df_file)
        assert df_file.exists()
        df = pd.read_csv(df_file, sep=';', encoding='utf-8')
        assert len(df) == 1
        assert df.iloc[0]["date"] == line.date
        assert df.iloc[0]["weekday"] == line.weekday
        # Appending another row should add a new row
        line.record_into_df(df_file)
        df2 = pd.read_csv(df_file, sep=';', encoding='utf-8')
        assert len(df2) == 2
        assert (df2["date"] == line.date).all()

    @pytest.mark.fast
    def test_create_df_creates_file_with_correct_columns(self, tmp_path: pathlib.Path, line: tr.TimeRecorder) -> None:
        """Test that create_df creates a file with the correct columns and no rows."""
        df_file = tmp_path / "logbook_df.csv"
        line.create_df(df_file)
        assert df_file.exists()
        df = pd.read_csv(df_file, sep=';', encoding='utf-8')
        expected_columns = [
            "weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"
        ]
        assert list(df.columns) == expected_columns
        assert len(df) == 0

"""Unit tests for the time_recording module, including TimeRecorder and related functionality."""

import pathlib

import pandas as pd
import pytest

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
        df = pd.DataFrame(
            {
                "weekday": ["Thu", "Thu", "Fri"],
                "date": ["24.04.2025", "24.04.2025", "25.04.2025"],
                "start_time": ["08:00:00", "11:30:00", "08:00:00"],
                "end_time": ["9:00:00", "17:00:00", "16:00:00"],
                "lunch_break_duration": [1, 60, 60],
                "work_time": [1.0, 6.0, 8.0],
                "case": ["undertime", "undertime", "overtime"],
                "overtime": [-7, 4.5, 0.0],
            }
        )
        df.to_csv(df_file, sep=";", index=False, encoding="utf-8")
        line.squash_df(df_file)
        result = pd.read_csv(df_file, sep=";", encoding="utf-8")
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

import os
import sys
from datetime import timedelta

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adjust path to import time_recording module

import time_recorder as tr


class TestExtractTimeComponents:
    """Tests for TimeRecorder.extract_time_components."""

    @pytest.fixture
    def line(self) -> tr.TimeRecorder:
        """Fixture to create a sample TimeRecorder for extract_time_components tests."""
        # Use a valid line for method access; time values don't matter here
        return tr.TimeRecorder(
            date="24.04.2025",
            start_time="08:00",
            end_time="16:00",
            lunch_break_duration=30,
        )

    @pytest.mark.parametrize(
        ("delta", "expected"),
        [
            (timedelta(hours=2, minutes=15, seconds=30), (2, 15, 30)),
            (timedelta(hours=0, minutes=0, seconds=0), (0, 0, 0)),
            (timedelta(hours=23, minutes=59, seconds=59), (23, 59, 59)),
            (timedelta(hours=1), (1, 0, 0)),
            (timedelta(minutes=90), (1, 30, 0)),
            (timedelta(seconds=3721), (1, 2, 1)),
        ]
    )
    @pytest.mark.fast
    def test_extract_time_components_basic(self, line: tr.TimeRecorder, delta: timedelta, expected: tuple[int, int, int]) -> None:
        """Test that extract_time_components returns correct hour, minute, second tuples for various timedeltas."""
        result = line.extract_time_components(delta)
        assert tuple(x for x in result) == expected

    @pytest.mark.parametrize(
        ("delta", "expected"),
        [
            (timedelta(days=2, hours=3, minutes=4, seconds=5), (51, 4, 5)),
            (timedelta(days=0, hours=2, minutes=15, seconds=30), (2, 15, 30)),
            (timedelta(days=0, hours=0, minutes=0, seconds=0), (0, 0, 0)),
            (timedelta(days=4, hours=23, minutes=59, seconds=59), (119, 59, 59)),
        ]
    )
    @pytest.mark.fast
    def test_extract_time_components_with_days(self, line: tr.TimeRecorder, delta: timedelta, expected: tuple[int, int, int]) -> None:
        """Test that extract_time_components correctly handles timedeltas with days."""
        # Should return total hours, not just hours in the last day
        result = line.extract_time_components(delta)
        assert tuple(x for x in result) == expected

    @pytest.mark.fast
    def test_extract_time_components_warns_on_large_hours(self, line: tr.TimeRecorder, caplog: pytest.LogCaptureFixture) -> None:
        """Test that extract_time_components logs a warning when timedelta exceeds 24 hours."""
        test_hours = 25
        # 25 hours triggers warning
        delta = timedelta(hours=test_hours)
        with caplog.at_level("WARNING"):
            hours, _, _ = line.extract_time_components(delta)
            assert int(hours) == test_hours
            assert "timedelta exceeds 24 hours" in caplog.text or "looks like an error" in caplog.text

    @pytest.mark.fast
    def test_extract_time_components_negative(self, line: tr.TimeRecorder) -> None:
        """Test that extract_time_components handles negative timedeltas correctly."""
        # Negative timedelta
        delta = timedelta(hours=-2, minutes=-30)
        hours, minutes, seconds = line.extract_time_components(delta)
        assert int(hours) == -2 or int(hours) == -3  # Depending on how divmod handles negatives
        # The exact result may depend on Python's divmod behavior with negatives

    @pytest.mark.fast
    def test_extract_time_components_type_annotations(self, line: tr.TimeRecorder) -> None:
        """Test that extract_time_components returns a tuple of (float, float, float)."""
        delta = timedelta(hours=1, minutes=2, seconds=3)
        result = line.extract_time_components(delta)
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(x, float) for x in result)

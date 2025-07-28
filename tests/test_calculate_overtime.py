from datetime import timedelta

import pytest

import time_recorder as tr


class TestCalculateOvertime:
    """Tests for TimeRecorder.calculate_overtime."""

    @pytest.fixture
    def line(self) -> tr.TimeRecorder:
        """Fixture to create a sample TimeRecorder for calculate_overtime tests."""
        return tr.TimeRecorder(
            date="24.04.2025",
            start_time="08:00",
            end_time="16:00",
            lunch_break_duration=0,
        )

    @pytest.mark.parametrize(
        ("work_time", "expected_case", "expected_delta"),
        [
            (timedelta(hours=8), "overtime", timedelta(hours=0)),
            (timedelta(hours=9, minutes=15), "overtime", timedelta(hours=1, minutes=15)),
            (timedelta(hours=8, minutes=1), "overtime", timedelta(minutes=1)),
            (timedelta(hours=7, minutes=59), "undertime", timedelta(minutes=1)),
            (timedelta(hours=0), "undertime", timedelta(hours=8)),
            (timedelta(hours=12), "overtime", timedelta(hours=4)),
        ],
    )
    @pytest.mark.fast
    def test_calculate_overtime_cases(self, line: tr.TimeRecorder, work_time: timedelta, expected_case: str, expected_delta: timedelta) -> None:
        """Test calculate_overtime returns correct case and timedelta."""
        case, overtime = line.calculate_overtime(work_time)
        assert case == expected_case
        assert overtime == expected_delta

    @pytest.mark.fast
    def test_calculate_overtime_negative_work_time(self, line: tr.TimeRecorder) -> None:
        """Test calculate_overtime with negative work_time returns undertime with increased delta."""
        case, overtime = line.calculate_overtime(timedelta(hours=-2))
        assert case == "undertime"
        assert overtime == timedelta(hours=10)

    @pytest.mark.fast
    def test_calculate_overtime_type_annotations(self, line: tr.TimeRecorder) -> None:
        """Test that calculate_overtime returns a tuple of (str, timedelta)."""
        case, overtime = line.calculate_overtime(timedelta(hours=8))
        assert isinstance(case, str)
        assert isinstance(overtime, timedelta)

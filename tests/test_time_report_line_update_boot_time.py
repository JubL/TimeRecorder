from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

import time_recorder as tr


class TestTimeRecorderUpdateBootTime:
    """Tests for TimeRecorder.update_boot_time."""

    @pytest.fixture
    def sample_line(self) -> tr.TimeRecorder:
        """Fixture to create a sample TimeRecorder for testing."""
        return tr.TimeRecorder(
            date="24.04.2025",
            start_time="07:32",
            end_time="15:40",
            lunch_break_duration=60,
        )

    @pytest.fixture
    def fake_boot_timestamp(self) -> datetime:
        """Fixture to provide a fake boot timestamp."""
        return datetime(2025, 4, 25, 6, 30, 0).timestamp()

    @pytest.mark.fast
    @patch("psutil.boot_time")
    def test_update_boot_time_sets_start_time_to_boot_time(self, mock_boot_time: Mock, sample_line: tr.TimeRecorder, fake_boot_timestamp: datetime) -> None:
        """Test that update_boot_time sets start_time to the system boot time."""
        mock_boot_time.return_value = fake_boot_timestamp

        old_end_time = sample_line.end_time

        sample_line.update_boot_time()

        assert sample_line.start_time == datetime.fromtimestamp(fake_boot_timestamp)
        # End time should have the same date as boot time, but same time as before
        assert sample_line.end_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
        assert sample_line.end_time.time() == old_end_time.time()
        # Work hours and overtime should be recalculated
        assert isinstance(sample_line.work_time, timedelta)
        assert sample_line.case in {"overtime", "undertime"}
        assert isinstance(sample_line.overtime, timedelta)

    @pytest.mark.fast
    @patch("psutil.boot_time")
    def test_update_boot_time_updates_weekday_and_date(self, mock_boot_time: Mock, sample_line: tr.TimeRecorder, fake_boot_timestamp: datetime) -> None:
        """Test that update_boot_time updates weekday and date to match the boot time."""
        mock_boot_time.return_value = fake_boot_timestamp

        sample_line.update_boot_time()

        # The start_time and end_time date should match the boot date
        assert sample_line.start_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
        assert sample_line.end_time.date() == datetime.fromtimestamp(fake_boot_timestamp).date()
        # The weekday should match the boot date's weekday
        expected_weekday = datetime.fromtimestamp(fake_boot_timestamp).strftime("%a")
        assert sample_line.weekday == expected_weekday

    @pytest.mark.fast
    @patch("psutil.boot_time")
    def test_update_boot_time_boot_time_none_raises(self, mock_boot_time: Mock, sample_line: tr.TimeRecorder) -> None:
        """Test that update_boot_time raises BootTimeError if boot_time is None."""
        mock_boot_time.return_value = None
        with pytest.raises(tr.BootTimeError, match="Failed to retrieve system boot time"):
            sample_line.update_boot_time()

    @pytest.mark.fast
    @patch("psutil.boot_time", side_effect=Exception("psutil error"))
    def test_update_boot_time_psutil_error(self, mock_boot_time: Mock, sample_line: tr.TimeRecorder) -> None:
        """Test that update_boot_time raises BootTimeError on psutil error."""
        # Use mock_boot_time to satisfy linter by asserting it was called
        with pytest.raises(tr.BootTimeError, match="Unexpected error while updating boot time: psutil error"):
            sample_line.update_boot_time()
        mock_boot_time.assert_called()

    @pytest.mark.fast
    @patch("psutil.boot_time")
    def test_update_boot_time_end_time_before_boot_time(self, mock_boot_time: Mock, sample_line: tr.TimeRecorder) -> None:
        """Test behavior if the original end time is before the boot time (should raise or handle gracefully)."""
        # Set a fake boot time after the original end time
        fake_boot_datetime = datetime(2025, 4, 26, 16, 0, 0)
        mock_boot_time.return_value = fake_boot_datetime.timestamp()
        # The original end_time is 2025-04-24 15:40, so this will make start_time after end_time
        with pytest.raises(tr.BootTimeError, match="The start time must be before the end time."):
            sample_line.update_boot_time()

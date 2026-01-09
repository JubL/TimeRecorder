"""Tests for argument parsing functionality."""

import sys
from unittest.mock import patch

import pytest

import src.arg_parser as ap


@pytest.mark.fast
def test_parse_args_no_arguments() -> None:
    """Test parsing with no arguments (default behavior)."""
    with patch.object(sys, "argv", ["test_script"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        # Check default values
        assert args.boot is None
        assert args.date is None
        assert args.start is None
        assert args.end is None
        assert args.end_now is False
        assert args.lunch is None
        assert args.log is None
        assert args.squash is None
        assert args.add_missing is None
        assert args.weekly is None
        assert args.tail is None
        assert args.config == "config.yaml"
        assert args.logbook is None
        assert args.plot is None
        assert args.num_months is None
        assert args.color_scheme is None


@pytest.mark.fast
def test_parse_args_boot_time() -> None:
    """Test parsing with --boot argument."""
    with patch.object(sys, "argv", ["test_script", "--boot"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.boot is True
        assert args.date is None
        assert args.start is None


@pytest.mark.fast
def test_parse_args_boot_time_false() -> None:
    """Test parsing with --no-boot argument."""
    with patch.object(sys, "argv", ["test_script", "--no-boot"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.boot is False


@pytest.mark.fast
def test_parse_args_date_and_start() -> None:
    """Test parsing with --date and --start arguments."""
    with patch.object(sys, "argv", ["test_script", "--date", "25.07.2025", "--start", "08:30"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.date == "25.07.2025"
        assert args.start == "08:30"
        assert args.boot is False


@pytest.mark.fast
def test_parse_args_end_time() -> None:
    """Test parsing with --end argument."""
    with patch.object(sys, "argv", ["test_script", "--end", "17:30"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.end == "17:30"
        assert args.end_now is False


@pytest.mark.fast
def test_parse_args_end_now() -> None:
    """Test parsing with --end_now argument."""
    with patch.object(sys, "argv", ["test_script", "--end_now"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.end_now is True
        assert args.end is None


@pytest.mark.fast
def test_parse_args_lunch_break() -> None:
    """Test parsing with --lunch argument."""
    with patch.object(sys, "argv", ["test_script", "--lunch", "45"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.lunch == 45


@pytest.mark.fast
def test_parse_args_logging() -> None:
    """Test parsing with --log argument."""
    with patch.object(sys, "argv", ["test_script", "--log"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.log is True


@pytest.mark.fast
def test_parse_args_squash_enable() -> None:
    """Test parsing with --squash argument."""
    with patch.object(sys, "argv", ["test_script", "--squash"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.squash is True


@pytest.mark.fast
def test_parse_args_squash_disable() -> None:
    """Test parsing with --no-squash argument."""
    with patch.object(sys, "argv", ["test_script", "--no-squash"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.squash is False


@pytest.mark.fast
def test_parse_args_add_missing_enable() -> None:
    """Test parsing with --add_missing argument."""
    with patch.object(sys, "argv", ["test_script", "--add_missing"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.add_missing is True


@pytest.mark.fast
def test_parse_args_add_missing_disable() -> None:
    """Test parsing with --no-add_missing argument."""
    with patch.object(sys, "argv", ["test_script", "--no-add_missing"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.add_missing is False


@pytest.mark.fast
def test_parse_args_weekly_enable() -> None:
    """Test parsing with --weekly argument."""
    with patch.object(sys, "argv", ["test_script", "--weekly"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.weekly is True


@pytest.mark.fast
def test_parse_args_weekly_disable() -> None:
    """Test parsing with --no-weekly argument."""
    with patch.object(sys, "argv", ["test_script", "--no-weekly"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.weekly is False


@pytest.mark.fast
def test_parse_args_tail() -> None:
    """Test parsing with --tail argument."""
    with patch.object(sys, "argv", ["test_script", "--tail", "10"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.tail == 10


@pytest.mark.fast
def test_parse_args_config_file() -> None:
    """Test parsing with --config argument."""
    with patch.object(sys, "argv", ["test_script", "--config", "my_config.yaml"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.config == "my_config.yaml"


@pytest.mark.fast
def test_parse_args_logbook_file() -> None:
    """Test parsing with --logbook argument."""
    with patch.object(sys, "argv", ["test_script", "--logbook", "my_logbook.txt"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.logbook == "my_logbook.txt"


@pytest.mark.fast
def test_parse_args_plot() -> None:
    """Test parsing with --plot argument."""
    with patch.object(sys, "argv", ["test_script", "--plot"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.plot is True


@pytest.mark.fast
def test_parse_args_num_months() -> None:
    """Test parsing with --num_months argument."""
    with patch.object(sys, "argv", ["test_script", "--num_months", "6"]):
        parser = ap.TimeRecorderArgumentParser()
        args = parser.parse_args()

        assert args.num_months == 6

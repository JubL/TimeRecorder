"""Tests for the run_arg_parser convenience function."""

import sys
from unittest.mock import patch

import pytest

import src.arg_parser as ap


@pytest.mark.fast
def test_run_arg_parser_no_arguments() -> None:
    """Test run_arg_parser with no arguments."""
    with patch.object(sys, "argv", ["test_script"]):
        args = ap.run_arg_parser()

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
def test_run_arg_parser_with_boot() -> None:
    """Test run_arg_parser with --boot argument."""
    with patch.object(sys, "argv", ["test_script", "--boot"]):
        args = ap.run_arg_parser()

        assert args.boot is True
        assert args.date is None
        assert args.start is None


@pytest.mark.fast
def test_run_arg_parser_with_date_start() -> None:
    """Test run_arg_parser with --date and --start arguments."""
    with patch.object(sys, "argv", ["test_script", "--date", "25.07.2025", "--start", "08:30"]):
        args = ap.run_arg_parser()

        assert args.date == "25.07.2025"
        assert args.start == "08:30"
        assert args.boot is None


@pytest.mark.fast
def test_run_arg_parser_with_end() -> None:
    """Test run_arg_parser with --end argument."""
    with patch.object(sys, "argv", ["test_script", "--end", "17:30"]):
        args = ap.run_arg_parser()

        assert args.end == "17:30"
        assert args.end_now is False


@pytest.mark.fast
def test_run_arg_parser_with_end_now() -> None:
    """Test run_arg_parser with --end_now argument."""
    with patch.object(sys, "argv", ["test_script", "--end_now"]):
        args = ap.run_arg_parser()

        assert args.end_now is True
        assert args.end is None


@pytest.mark.fast
def test_run_arg_parser_with_lunch() -> None:
    """Test run_arg_parser with --lunch argument."""
    with patch.object(sys, "argv", ["test_script", "--lunch", "45"]):
        args = ap.run_arg_parser()

        assert args.lunch == 45


@pytest.mark.fast
def test_run_arg_parser_with_log() -> None:
    """Test run_arg_parser with --log argument."""
    with patch.object(sys, "argv", ["test_script", "--log"]):
        args = ap.run_arg_parser()

        assert args.log is True


@pytest.mark.fast
def test_run_arg_parser_with_squash() -> None:
    """Test run_arg_parser with --squash argument."""
    with patch.object(sys, "argv", ["test_script", "--squash"]):
        args = ap.run_arg_parser()

        assert args.squash is True


@pytest.mark.fast
def test_run_arg_parser_with_add_missing() -> None:
    """Test run_arg_parser with --add_missing argument."""
    with patch.object(sys, "argv", ["test_script", "--add_missing"]):
        args = ap.run_arg_parser()

        assert args.add_missing is True


@pytest.mark.fast
def test_run_arg_parser_with_weekly() -> None:
    """Test run_arg_parser with --weekly argument."""
    with patch.object(sys, "argv", ["test_script", "--weekly"]):
        args = ap.run_arg_parser()

        assert args.weekly is True


@pytest.mark.fast
def test_run_arg_parser_with_tail() -> None:
    """Test run_arg_parser with --tail argument."""
    with patch.object(sys, "argv", ["test_script", "--tail", "10"]):
        args = ap.run_arg_parser()

        assert args.tail == 10


@pytest.mark.fast
def test_run_arg_parser_with_config() -> None:
    """Test run_arg_parser with --config argument."""
    with patch.object(sys, "argv", ["test_script", "--config", "my_config.yaml"]):
        args = ap.run_arg_parser()

        assert args.config == "my_config.yaml"


@pytest.mark.fast
def test_run_arg_parser_with_logbook() -> None:
    """Test run_arg_parser with --logbook argument."""
    with patch.object(sys, "argv", ["test_script", "--logbook", "my_logbook.txt"]):
        args = ap.run_arg_parser()

        assert args.logbook == "my_logbook.txt"


@pytest.mark.fast
def test_run_arg_parser_with_plot() -> None:
    """Test run_arg_parser with --plot argument."""
    with patch.object(sys, "argv", ["test_script", "--plot"]):
        args = ap.run_arg_parser()

        assert args.plot is True


@pytest.mark.fast
def test_run_arg_parser_with_num_months() -> None:
    """Test run_arg_parser with --num_months argument."""
    with patch.object(sys, "argv", ["test_script", "--num_months", "6"]):
        args = ap.run_arg_parser()

        assert args.num_months == 6


@pytest.mark.fast
def test_run_arg_parser_new_instance_created() -> None:
    """Test that run_arg_parser creates a new parser instance each time."""
    with patch.object(sys, "argv", ["test_script"]):
        args1 = ap.run_arg_parser()
        args2 = ap.run_arg_parser()

        # Both should have the same default values
        assert args1.boot == args2.boot
        assert args1.date == args2.date
        assert args1.start == args2.start
        assert args1.end == args2.end
        assert args1.end_now == args2.end_now
        assert args1.lunch == args2.lunch
        assert args1.log == args2.log
        assert args1.squash == args2.squash
        assert args1.add_missing == args2.add_missing
        assert args1.weekly == args2.weekly
        assert args1.tail == args2.tail
        assert args1.config == args2.config
        assert args1.logbook == args2.logbook
        assert args1.plot == args2.plot
        assert args1.num_months == args2.num_months
        assert args1.color_scheme == args2.color_scheme

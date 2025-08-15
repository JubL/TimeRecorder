"""Integration tests for the TimeRecorderArgumentParser."""

import sys
from unittest.mock import patch

import pytest

import src.arg_parser as ap


@pytest.mark.fast
@pytest.mark.integration
def test_basic_time_recording_workflow() -> None:
    """Test a basic time recording workflow."""
    with patch.object(sys, "argv", ["test_script", "--boot", "--end", "17:30"]):
        args = ap.run_arg_parser()

        assert args.boot is True
        assert args.end == "17:30"
        assert args.date is None
        assert args.start is None
        assert args.end_now is False
        assert args.lunch is None
        assert args.log is None


@pytest.mark.fast
@pytest.mark.integration
def test_manual_time_recording_workflow() -> None:
    """Test a manual time recording workflow."""
    with patch.object(sys, "argv", ["test_script", "--date", "25.07.2025", "--start", "08:30", "--end", "17:30"]):
        args = ap.run_arg_parser()

        assert args.date == "25.07.2025"
        assert args.start == "08:30"
        assert args.end == "17:30"
        assert args.boot is None
        assert args.end_now is False


@pytest.mark.fast
@pytest.mark.integration
def test_visualization_workflow() -> None:
    """Test a visualization workflow."""
    with patch.object(sys, "argv", ["test_script", "--plot", "--color_scheme", "forest", "--num_months", "6"]):
        args = ap.run_arg_parser()

        assert args.plot is True
        assert args.color_scheme == "forest"
        assert args.num_months == 6
        assert args.boot is None
        assert args.date is None


@pytest.mark.fast
@pytest.mark.integration
def test_combined_workflow() -> None:
    """Test a combined workflow with time recording and visualization."""
    with patch.object(
        sys,
        "argv",
        [
            "test_script",
            "--boot",
            "--end",
            "17:30",
            "--lunch",
            "45",
            "--log",
            "--plot",
            "--color_scheme",
            "sunset",
        ],
    ):
        args = ap.run_arg_parser()

        assert args.boot is True
        assert args.end == "17:30"
        assert args.lunch == 45
        assert args.log is True
        assert args.plot is True
        assert args.color_scheme == "sunset"


@pytest.mark.fast
@pytest.mark.integration
def test_data_processing_workflow() -> None:
    """Test a data processing workflow."""
    with patch.object(sys, "argv", ["test_script", "--squash", "--add_missing", "--weekly", "--tail", "10"]):
        args = ap.run_arg_parser()

        assert args.squash is True
        assert args.add_missing is True
        assert args.weekly is True
        assert args.tail == 10


@pytest.mark.fast
@pytest.mark.integration
def test_custom_configuration_workflow() -> None:
    """Test a custom configuration workflow."""
    with patch.object(
        sys,
        "argv",
        ["test_script", "--config", "custom_config.yaml", "--logbook", "custom_logbook.txt"],
    ):
        args = ap.run_arg_parser()

        assert args.config == "custom_config.yaml"
        assert args.logbook == "custom_logbook.txt"


@pytest.mark.fast
@pytest.mark.integration
def test_end_now_workflow() -> None:
    """Test the end_now workflow."""
    with patch.object(sys, "argv", ["test_script", "--boot", "--end_now"]):
        args = ap.run_arg_parser()

        assert args.boot is True
        assert args.end_now is True
        assert args.end is None


@pytest.mark.fast
@pytest.mark.integration
def test_disabled_features_workflow() -> None:
    """Test workflow with disabled features."""
    with patch.object(sys, "argv", ["test_script", "--no-squash", "--no-add_missing", "--no-weekly"]):
        args = ap.run_arg_parser()

        assert args.squash is False
        assert args.add_missing is False
        assert args.weekly is False


@pytest.mark.fast
@pytest.mark.integration
def test_all_color_schemes_integration() -> None:
    """Test integration with all color schemes."""
    color_schemes = ["ocean", "forest", "sunset", "lavender", "coral"]

    for scheme in color_schemes:
        with patch.object(sys, "argv", ["test_script", "--plot", "--color_scheme", scheme]):
            args = ap.run_arg_parser()
            assert args.plot is True
            assert args.color_scheme == scheme


@pytest.mark.fast
@pytest.mark.integration
def test_edge_cases_empty_arguments() -> None:
    """Test edge case with empty arguments."""
    with patch.object(sys, "argv", ["test_script"]):
        args = ap.run_arg_parser()

        # All should be default values
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
        assert args.plot is False
        assert args.num_months is None
        assert args.color_scheme is None


@pytest.mark.fast
@pytest.mark.integration
def test_edge_cases_maximum_arguments() -> None:
    """Test edge case with maximum number of arguments."""
    with patch.object(
        sys,
        "argv",
        [
            "test_script",
            "--boot",
            "--end",
            "23:59:59",
            "--lunch",
            "999",
            "--log",
            "--squash",
            "--add_missing",
            "--weekly",
            "--tail",
            "1000",
            "--config",
            "config.yaml",
            "--logbook",
            "logbook.txt",
            "--plot",
            "--num_months",
            "100",
            "--color_scheme",
            "coral",
        ],
    ):
        args = ap.run_arg_parser()

        assert args.boot is True
        assert args.end == "23:59:59"
        assert args.lunch == 999
        assert args.log is True
        assert args.squash is True
        assert args.add_missing is True
        assert args.weekly is True
        assert args.tail == 1000
        assert args.config == "config.yaml"
        assert args.logbook == "logbook.txt"
        assert args.plot is True
        assert args.num_months == 100
        assert args.color_scheme == "coral"


@pytest.mark.fast
@pytest.mark.integration
def test_validation_warnings_integration() -> None:
    """Test integration with validation warnings."""
    with (
        patch.object(sys, "argv", ["test_script", "--boot", "--date", "25.07.2025", "--end", "17:30", "--end_now"]),
        patch("src.arg_parser.logger") as mock_logger,
    ):
        args = ap.run_arg_parser()

        # Should still parse successfully but with warnings
        assert args.boot is True
        assert args.date == "25.07.2025"
        assert args.end == "17:30"
        assert args.end_now is True

        # Should have multiple warnings
        assert mock_logger.warning.call_count >= 2


@pytest.mark.fast
@pytest.mark.integration
def test_boolean_optional_arguments_integration() -> None:
    """Test integration with boolean optional arguments."""
    with patch.object(
        sys,
        "argv",
        [
            "test_script",
            "--boot",
            "--no-squash",
            "--add_missing",
            "--no-weekly",
            "--log",
        ],
    ):
        args = ap.run_arg_parser()

        assert args.boot is True
        assert args.squash is False
        assert args.add_missing is True
        assert args.weekly is False
        assert args.log is True


@pytest.mark.fast
@pytest.mark.integration
def test_argument_order_independence() -> None:
    """Test that argument order doesn't affect parsing."""
    # Test with different argument orders
    test_orders = [
        ["--boot", "--end", "17:30", "--log"],
        ["--end", "17:30", "--boot", "--log"],
        ["--log", "--boot", "--end", "17:30"],
        ["--end", "17:30", "--log", "--boot"],
    ]

    for order in test_orders:
        with patch.object(sys, "argv", ["test_script", *order]):
            args = ap.run_arg_parser()

            assert args.boot is True
            assert args.end == "17:30"
            assert args.log is True


@pytest.mark.fast
@pytest.mark.integration
def test_duplicate_arguments_handling() -> None:
    """Test handling of duplicate arguments."""
    with patch.object(sys, "argv", ["test_script", "--boot", "--boot", "--end", "17:30", "--end", "18:30"]):
        args = ap.run_arg_parser()

        # Should use the last occurrence of each argument
        assert args.boot is True
        assert args.end == "18:30"


@pytest.mark.fast
@pytest.mark.integration
def test_mixed_valid_invalid_arguments() -> None:
    """Test handling of mixed valid and invalid arguments."""
    with patch.object(sys, "argv", ["test_script", "--boot", "--invalid_arg", "--end", "17:30"]), pytest.raises(SystemExit):
        ap.run_arg_parser()


@pytest.mark.fast
@pytest.mark.integration
def test_help_and_version_arguments() -> None:
    """Test help and version arguments."""
    # Test --help
    with patch.object(sys, "argv", ["test_script", "--help"]), pytest.raises(SystemExit):
        ap.run_arg_parser()

    # Test --version
    with patch.object(sys, "argv", ["test_script", "--version"]), pytest.raises(SystemExit):
        ap.run_arg_parser()


@pytest.mark.fast
@pytest.mark.integration
def test_numeric_argument_boundaries() -> None:
    """Test numeric argument boundaries."""
    # Test minimum values
    with patch.object(sys, "argv", ["test_script", "--lunch", "0", "--tail", "0", "--num_months", "0"]):
        args = ap.run_arg_parser()
        assert args.lunch == 0
        assert args.tail == 0
        assert args.num_months == 0

    # Test large values
    with patch.object(sys, "argv", ["test_script", "--lunch", "999999", "--tail", "999999", "--num_months", "999999"]):
        args = ap.run_arg_parser()
        assert args.lunch == 999999
        assert args.tail == 999999
        assert args.num_months == 999999


@pytest.mark.fast
@pytest.mark.integration
def test_string_argument_boundaries() -> None:
    """Test string argument boundaries."""
    # Test empty strings
    with patch.object(sys, "argv", ["test_script", "--date", "", "--start", "", "--end", ""]):
        args = ap.run_arg_parser()
        assert not args.date
        assert not args.start
        assert not args.end

    # Test very long strings
    long_string = "a" * 1000
    with patch.object(sys, "argv", ["test_script", "--date", long_string, "--start", long_string, "--end", long_string]):
        args = ap.run_arg_parser()
        assert args.date == long_string
        assert args.start == long_string
        assert args.end == long_string


@pytest.mark.fast
@pytest.mark.integration
def test_unicode_argument_handling() -> None:
    """Test handling of unicode arguments."""
    unicode_string = "25.07.2025 🕐 08:30 🕐 17:30"
    with patch.object(sys, "argv", ["test_script", "--date", unicode_string, "--start", unicode_string, "--end", unicode_string]):
        args = ap.run_arg_parser()
        assert args.date == unicode_string
        assert args.start == unicode_string
        assert args.end == unicode_string

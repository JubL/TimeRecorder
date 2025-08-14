"""Tests for argument validation functionality."""

import sys
from unittest.mock import Mock, patch

import pytest

import src.arg_parser as ap


@pytest.mark.fast
def test_validate_time_arguments_boot_only() -> None:
    """Test validation with only --boot argument (valid case)."""
    args = Mock()
    args.boot = True
    args.date = None
    args.start = None
    args.end = None
    args.end_now = False

    # Should not raise any warnings
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_date_start_only() -> None:
    """Test validation with only --date and --start arguments (valid case)."""
    args = Mock()
    args.boot = None
    args.date = "25.07.2025"
    args.start = "08:30"
    args.end = None
    args.end_now = False

    # Should not raise any warnings
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_boot_with_date_warning() -> None:
    """Test validation with --boot and --date (should warn)."""
    args = Mock()
    args.boot = True
    args.date = "25.07.2025"
    args.start = None
    args.end = None
    args.end_now = False

    with patch("src.arg_parser.logger") as mock_logger:
        ap.TimeRecorderArgumentParser.validate_time_arguments(args)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "does not make much sense" in warning_message
        assert "--boot" in warning_message
        assert "--date" in warning_message


@pytest.mark.fast
def test_validate_time_arguments_boot_with_start_warning() -> None:
    """Test validation with --boot and --start (should warn)."""
    args = Mock()
    args.boot = True
    args.date = None
    args.start = "08:30"
    args.end = None
    args.end_now = False

    with patch("src.arg_parser.logger") as mock_logger:
        ap.TimeRecorderArgumentParser.validate_time_arguments(args)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "does not make much sense" in warning_message
        assert "--boot" in warning_message
        assert "--start" in warning_message


@pytest.mark.fast
def test_validate_time_arguments_boot_with_both_date_start_warning() -> None:
    """Test validation with --boot, --date, and --start (should warn)."""
    args = Mock()
    args.boot = True
    args.date = "25.07.2025"
    args.start = "08:30"
    args.end = None
    args.end_now = False

    with patch("src.arg_parser.logger") as mock_logger:
        ap.TimeRecorderArgumentParser.validate_time_arguments(args)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "does not make much sense" in warning_message
        assert "--boot" in warning_message
        assert "--date" in warning_message
        assert "--start" in warning_message


@pytest.mark.fast
def test_validate_time_arguments_date_only_warning() -> None:
    """Test validation with only --date (should warn)."""
    args = Mock()
    args.boot = None
    args.date = "25.07.2025"
    args.start = None
    args.end = None
    args.end_now = False

    with patch("src.arg_parser.logger") as mock_logger:
        ap.TimeRecorderArgumentParser.validate_time_arguments(args)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "both --date and --start must be provided" in warning_message


@pytest.mark.fast
def test_validate_time_arguments_start_only_warning() -> None:
    """Test validation with only --start (should warn)."""
    args = Mock()
    args.boot = None
    args.date = None
    args.start = "08:30"
    args.end = None
    args.end_now = False

    with patch("src.arg_parser.logger") as mock_logger:
        ap.TimeRecorderArgumentParser.validate_time_arguments(args)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "both --date and --start must be provided" in warning_message


@pytest.mark.fast
def test_validate_time_arguments_end_and_end_now_warning() -> None:
    """Test validation with both --end and --end_now (should warn)."""
    args = Mock()
    args.boot = None
    args.date = None
    args.start = None
    args.end = "17:30"
    args.end_now = True

    with patch("src.arg_parser.logger") as mock_logger:
        ap.TimeRecorderArgumentParser.validate_time_arguments(args)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "does not make much sense" in warning_message
        assert "--end" in warning_message
        assert "--end_now" in warning_message


@pytest.mark.fast
def test_validate_time_arguments_end_only() -> None:
    """Test validation with only --end (valid case)."""
    args = Mock()
    args.boot = None
    args.date = None
    args.start = None
    args.end = "17:30"
    args.end_now = False

    # Should not raise any warnings
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_end_now_only() -> None:
    """Test validation with only --end_now (valid case)."""
    args = Mock()
    args.boot = None
    args.date = None
    args.start = None
    args.end = None
    args.end_now = True

    # Should not raise any warnings
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_no_time_specification() -> None:
    """Test validation with no time specification (valid case)."""
    args = Mock()
    args.boot = None
    args.date = None
    args.start = None
    args.end = None
    args.end_now = False

    # Should not raise any warnings
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_complex_valid_combination() -> None:
    """Test validation with a complex but valid combination."""
    args = Mock()
    args.boot = True
    args.date = None
    args.start = None
    args.end = "17:30"
    args.end_now = False

    # Should not raise any warnings (boot + end is valid)
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_complex_invalid_combination() -> None:
    """Test validation with a complex invalid combination."""
    args = Mock()
    args.boot = True
    args.date = "25.07.2025"
    args.start = "08:30"
    args.end = "17:30"
    args.end_now = True

    with patch("src.arg_parser.logger") as mock_logger:
        ap.TimeRecorderArgumentParser.validate_time_arguments(args)
        # Should warn twice: once for boot+date/start, once for end+end_now
        assert mock_logger.warning.call_count == 2


@pytest.mark.fast
def test_validate_time_arguments_string_validation() -> None:
    """Test validation with string type checking."""
    args = Mock()
    args.boot = None
    args.date = "25.07.2025"  # Valid string
    args.start = "08:30"  # Valid string
    args.end = None
    args.end_now = False

    # Should not raise any warnings
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_empty_string_validation() -> None:
    """Test validation with empty strings."""
    args = Mock()
    args.boot = None
    args.date = ""  # Empty string should be treated as None
    args.start = ""  # Empty string should be treated as None
    args.end = ""
    args.end_now = False

    # Should not raise any warnings (empty strings are treated as None)
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_whitespace_string_validation() -> None:
    """Test validation with whitespace-only strings."""
    args = Mock()
    args.boot = None
    args.date = "   "  # Whitespace-only string
    args.start = "   "  # Whitespace-only string
    args.end = "   "
    args.end_now = False

    # Should not raise any warnings (whitespace strings are still strings)
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_boolean_validation() -> None:
    """Test validation with boolean values."""
    args = Mock()
    args.boot = False  # Explicit False
    args.date = None
    args.start = None
    args.end = None
    args.end_now = False

    # Should not raise any warnings
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
def test_validate_time_arguments_none_values() -> None:
    """Test validation with None values."""
    args = Mock()
    args.boot = None
    args.date = None
    args.start = None
    args.end = None
    args.end_now = None

    # Should not raise any warnings
    ap.TimeRecorderArgumentParser.validate_time_arguments(args)


@pytest.mark.fast
@pytest.mark.integration
def test_validate_time_arguments_integration_with_parse_args() -> None:
    """Test validation integration with parse_args method."""
    with patch.object(sys, "argv", ["test_script", "--boot", "--date", "25.07.2025"]):
        parser = ap.TimeRecorderArgumentParser()

        with patch("src.arg_parser.logger") as mock_logger:
            _ = parser.parse_args()
            mock_logger.warning.assert_called_once()
            warning_message = mock_logger.warning.call_args[0][0]
            assert "does not make much sense" in warning_message


@pytest.mark.fast
@pytest.mark.integration
def test_validate_time_arguments_integration_end_conflict() -> None:
    """Test validation integration with end time conflict."""
    with patch.object(sys, "argv", ["test_script", "--end", "17:30", "--end_now"]):
        parser = ap.TimeRecorderArgumentParser()

        with patch("src.arg_parser.logger") as mock_logger:
            _ = parser.parse_args()
            mock_logger.warning.assert_called_once()
            warning_message = mock_logger.warning.call_args[0][0]
            assert "does not make much sense" in warning_message

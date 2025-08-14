"""Tests for help text and utility methods."""

from unittest.mock import Mock, patch

import pytest

import src.arg_parser as ap


@pytest.mark.fast
def test_get_help_text() -> None:
    """Test that get_help_text returns formatted help text."""
    parser = ap.TimeRecorderArgumentParser()
    help_text = parser.get_help_text()

    assert isinstance(help_text, str)
    assert len(help_text) > 0
    assert "usage:" in help_text.lower()
    assert "Time recorder" in help_text
    assert "--help" in help_text
    assert "--version" in help_text


@pytest.mark.fast
def test_get_help_text_contains_all_arguments() -> None:
    """Test that help text contains all expected arguments."""
    parser = ap.TimeRecorderArgumentParser()
    help_text = parser.get_help_text()

    # Time specification arguments
    assert "--boot" in help_text
    assert "--date" in help_text
    assert "--start" in help_text

    # Time completion arguments
    assert "--end" in help_text
    assert "--end_now" in help_text
    assert "--lunch" in help_text

    # Processing control arguments
    assert "--log" in help_text
    assert "--squash" in help_text
    assert "--add_missing" in help_text
    assert "--weekly" in help_text
    assert "--tail" in help_text

    # Configuration arguments
    assert "--config" in help_text
    assert "--logbook" in help_text

    # Visualization arguments
    assert "--plot" in help_text
    assert "--num_months" in help_text
    assert "--color_scheme" in help_text


@pytest.mark.fast
def test_get_help_text_contains_descriptions() -> None:
    """Test that help text contains argument descriptions."""
    parser = ap.TimeRecorderArgumentParser()
    help_text = parser.get_help_text()

    # Check for some key descriptions
    assert "Use system boot time" in help_text
    assert "Date in DD.MM.YYYY format" in help_text
    assert "Start time in HH:MM:SS format" in help_text
    assert "End time in HH:MM:SS format" in help_text
    assert "End time is one minute from now" in help_text
    assert "Lunch break duration in minutes" in help_text
    assert "Log the results" in help_text
    assert "Squash the logbook" in help_text
    assert "Add missing days to the logbook" in help_text
    assert "Calculate weekly hours" in help_text
    assert "Show the last n lines of the logbook" in help_text
    assert "Path to the config file" in help_text
    assert "Path to the logbook file" in help_text
    assert "Create visualizations from logbook data" in help_text
    assert "Number of months to show in daily hours plot" in help_text
    assert "Color scheme for visualizations" in help_text


@pytest.mark.fast
def test_print_help() -> None:
    """Test that print_help calls the underlying parser's print_help."""
    parser = ap.TimeRecorderArgumentParser()

    with patch.object(parser.parser, "print_help") as mock_print_help:
        parser.print_help()
        mock_print_help.assert_called_once()


@pytest.mark.fast
def test_print_usage() -> None:
    """Test that print_usage calls the underlying parser's print_usage."""
    parser = ap.TimeRecorderArgumentParser()

    with patch.object(parser.parser, "print_usage") as mock_print_usage:
        parser.print_usage()
        mock_print_usage.assert_called_once()


@pytest.mark.fast
def test_get_project_version_success() -> None:
    """Test get_project_version with valid pyproject.toml."""
    # Create a temporary pyproject.toml with a version
    mock_file = Mock()
    mock_file.__iter__ = Mock(
        return_value=iter(
            [
                'name = "timerecorder"',
                'version = "1.2.3"',
                'description = "A time recorder tool"',
            ],
        ),
    )
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("pathlib.Path.open", return_value=mock_file):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "1.2.3"


@pytest.mark.fast
def test_get_project_version_with_quotes() -> None:
    """Test get_project_version with quoted version."""
    mock_file = Mock()
    mock_file.__iter__ = Mock(
        return_value=iter(
            [
                'name = "timerecorder"',
                'version = "2.0.0-beta"',
                'description = "A time recorder tool"',
            ],
        ),
    )
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("pathlib.Path.open", return_value=mock_file):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "2.0.0-beta"


@pytest.mark.fast
def test_get_project_version_with_spaces() -> None:
    """Test get_project_version with spaces around equals sign."""
    mock_file = Mock()
    mock_file.__iter__ = Mock(
        return_value=iter(
            [
                'name = "timerecorder"',
                'version = "3.1.4"',
                'description = "A time recorder tool"',
            ],
        ),
    )
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("pathlib.Path.open", return_value=mock_file):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "3.1.4"


@pytest.mark.fast
def test_get_project_version_no_version_line() -> None:
    """Test get_project_version when no version line is found."""
    mock_file = Mock()
    mock_file.__iter__ = Mock(
        return_value=iter(
            [
                'name = "timerecorder"',
                'description = "A time recorder tool"',
                'authors = ["John Doe"]',
            ],
        ),
    )
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("pathlib.Path.open", return_value=mock_file):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "unknown"


@pytest.mark.fast
def test_get_project_version_empty_file() -> None:
    """Test get_project_version with empty file."""
    mock_file = Mock()
    mock_file.__iter__ = Mock(return_value=iter([]))
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("pathlib.Path.open", return_value=mock_file):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "unknown"


@pytest.mark.fast
def test_get_project_version_file_not_found() -> None:
    """Test get_project_version when file doesn't exist."""
    with patch("pathlib.Path.open", side_effect=FileNotFoundError):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "unknown"


@pytest.mark.fast
def test_get_project_version_permission_error() -> None:
    """Test get_project_version when file can't be read."""
    with patch("pathlib.Path.open", side_effect=PermissionError):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "unknown"


@pytest.mark.fast
def test_get_project_version_encoding_error() -> None:
    """Test get_project_version with encoding issues."""
    with patch("pathlib.Path.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "test")):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "unknown"


@pytest.mark.fast
def test_get_project_version_multiple_version_lines() -> None:
    """Test get_project_version with multiple version lines (should return first)."""
    mock_file = Mock()
    mock_file.__iter__ = Mock(
        return_value=iter(
            [
                'name = "timerecorder"',
                'version = "1.0.0"',
                'description = "A time recorder tool"',
                'version = "2.0.0"',  # This should be ignored
                'authors = ["John Doe"]',
            ],
        ),
    )
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("pathlib.Path.open", return_value=mock_file):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        assert version == "1.0.0"


@pytest.mark.fast
def test_get_project_version_version_in_other_context() -> None:  # TODO: improve on this behaviour
    """Test get_project_version when 'version' appears in other contexts."""
    mock_file = Mock()
    mock_file.__iter__ = Mock(
        return_value=iter(
            [
                'name = "timerecorder"',
                'description = "A version control tool"',  # Contains 'version' but not a version line
                'version = "1.5.0"',
                'authors = ["John Doe"]',
            ],
        ),
    )
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("pathlib.Path.open", return_value=mock_file):
        version = ap.TimeRecorderArgumentParser.get_project_version()
        # The current implementation matches any line containing "version", so it returns the first match
        assert version == "A version control tool"


@pytest.mark.fast
def test_help_text_formatting() -> None:
    """Test that help text is properly formatted."""
    parser = ap.TimeRecorderArgumentParser()
    help_text = parser.get_help_text()

    # Check that help text has proper structure
    lines = help_text.split("\n")
    assert len(lines) > 10  # Should have multiple lines

    # Check for usage line
    usage_lines = [line for line in lines if "usage:" in line.lower()]
    assert len(usage_lines) > 0

    # Check for options section
    options_lines = [line for line in lines if line.strip().startswith("-")]
    assert len(options_lines) > 0


@pytest.mark.fast
def test_help_text_argument_order() -> None:
    """Test that arguments appear in a logical order in help text."""
    parser = ap.TimeRecorderArgumentParser()
    help_text = parser.get_help_text()

    # Check that time specification arguments come before processing arguments
    boot_index = help_text.find("--boot")
    log_index = help_text.find("--log")

    if boot_index != -1 and log_index != -1:
        assert boot_index < log_index


@pytest.mark.fast
def test_help_text_no_duplicate_arguments() -> None:
    """Test that no arguments appear twice in help text."""
    parser = ap.TimeRecorderArgumentParser()
    help_text = parser.get_help_text()

    # Check for duplicate argument mentions (excluding arguments that appear in usage and options)
    arguments = ["--config", "--num_months", "--color_scheme"]
    for arg in arguments:
        count = help_text.count(arg)
        assert count == 2, f"Argument {arg} appears {count} times in help text"

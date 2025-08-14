"""Tests for the TimeRecorderArgumentParser constructor."""

import pytest

import src.arg_parser as ap


@pytest.mark.fast
def test_constructor_initialization() -> None:
    """Test that the constructor properly initializes the parser."""
    parser = ap.TimeRecorderArgumentParser()

    assert parser is not None
    assert hasattr(parser, "parser")
    assert parser.parser is not None


@pytest.mark.fast
def test_parser_description() -> None:
    """Test that the parser has the correct description."""
    parser = ap.TimeRecorderArgumentParser()

    help_text = parser.get_help_text()
    assert "Time recorder" in help_text
    assert "powerful and flexible Python tool" in help_text


@pytest.mark.fast
def test_parser_formatter_class() -> None:
    """Test that the parser uses the correct formatter class."""
    parser = ap.TimeRecorderArgumentParser()

    # Check that the formatter is set (it's a lambda function)
    assert parser.parser.formatter_class is not None
    # The formatter is a lambda function, so we can't check the name directly
    # But we can verify it's callable
    assert callable(parser.parser.formatter_class)


@pytest.mark.fast
def test_parser_width_setting() -> None:
    """Test that the parser has the correct width setting."""
    parser = ap.TimeRecorderArgumentParser()

    # The formatter should be configured with width=105
    help_text = parser.get_help_text()
    # We can't directly test the width, but we can verify the formatter is working
    assert len(help_text) > 0


@pytest.mark.fast
def test_parser_arguments_initialized() -> None:
    """Test that all expected arguments are initialized."""
    parser = ap.TimeRecorderArgumentParser()

    # Check that the parser has the expected argument groups
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

    # Version argument
    assert "--version" in help_text


@pytest.mark.fast
def test_multiple_instances_independent() -> None:
    """Test that multiple parser instances are independent."""
    parser1 = ap.TimeRecorderArgumentParser()
    parser2 = ap.TimeRecorderArgumentParser()

    assert parser1 is not parser2
    assert parser1.parser is not parser2.parser

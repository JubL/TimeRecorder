"""Tests for the get_display_config function in config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_display_config_complete(sample_config: dict) -> None:
    """Test extraction of complete display configuration."""
    config = {**sample_config, "display": {**sample_config["display"], "show_tail": 5}}

    result = cu.get_display_config(config)

    assert result["show_tail"] == 5


@pytest.mark.fast
def test_get_display_config_missing_display_section(sample_config: dict) -> None:
    """Test extraction when display section is missing from config."""
    config = {k: v for k, v in sample_config.items() if k != "display"}

    result = cu.get_display_config(config)

    # All values should be None when display section is missing
    assert result["show_tail"] is None


@pytest.mark.fast
def test_get_display_config_empty_display_section(sample_config: dict) -> None:
    """Test extraction when display section exists but is empty."""
    config = {**sample_config, "display": {}}

    result = cu.get_display_config(config)

    # All values should be None when display section is empty
    assert result["show_tail"] is None


@pytest.mark.fast
def test_get_display_config_with_other_sections(sample_config: dict) -> None:
    """Test extraction when config contains other sections alongside display."""
    config = {**sample_config, "display": {**sample_config["display"], "show_tail": 3}}

    result = cu.get_display_config(config)

    assert result["show_tail"] == 3


@pytest.mark.fast
def test_get_display_config_return_structure(sample_config: dict) -> None:
    """Test that the function returns the expected dictionary structure."""
    config = {**sample_config, "display": {**sample_config["display"], "show_tail": 7}}

    result = cu.get_display_config(config)

    # Check that result is a dictionary with exactly the expected keys
    assert isinstance(result, dict)
    assert set(result.keys()) == {"show_tail"}

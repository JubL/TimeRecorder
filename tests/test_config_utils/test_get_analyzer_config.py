"""Tests for the get_analyzer_config function in config_utils module."""

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_get_analyzer_config_complete(sample_config: dict) -> None:
    """Test get_analyzer_config with a complete configuration."""
    result = cu.get_analyzer_config(sample_config)

    expected = {
        "analyze_work_patterns": True,
        "standard_work_hours": 8,
        "work_days": [0, 1, 2, 3, 4],
    }

    assert result == expected


@pytest.mark.fast
def test_get_analyzer_config_missing_analyzer_section() -> None:
    """Test get_analyzer_config when analyzer section is missing."""
    config = {
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
        },
    }

    result = cu.get_analyzer_config(config)

    expected = {
        "analyze_work_patterns": None,
        "standard_work_hours": 8,
        "work_days": [0, 1, 2, 3, 4],
    }

    assert result == expected


@pytest.mark.fast
def test_get_analyzer_config_missing_work_schedule_section() -> None:
    """Test get_analyzer_config when work_schedule section is missing."""
    config = {
        "analyzer": {
            "analyze_work_patterns": True,
        },
    }

    result = cu.get_analyzer_config(config)

    expected = {
        "analyze_work_patterns": True,
        "standard_work_hours": None,
        "work_days": None,
    }

    assert result == expected


@pytest.mark.fast
def test_get_analyzer_config_empty_config() -> None:
    """Test get_analyzer_config with an empty configuration."""
    config: dict = {}

    result = cu.get_analyzer_config(config)

    expected = {
        "analyze_work_patterns": None,
        "standard_work_hours": None,
        "work_days": None,
    }

    assert result == expected


@pytest.mark.fast
def test_get_analyzer_config_partial_config() -> None:
    """Test get_analyzer_config with partial configuration."""
    config = {
        "analyzer": {
            "analyze_work_patterns": False,
        },
        "work_schedule": {
            "standard_work_hours": 7.5,
            "work_days": [1, 2, 3, 4, 5],
        },
    }

    result = cu.get_analyzer_config(config)

    expected = {
        "analyze_work_patterns": False,
        "standard_work_hours": 7.5,
        "work_days": [1, 2, 3, 4, 5],
    }

    assert result == expected


@pytest.mark.fast
def test_get_analyzer_config_none_values() -> None:
    """Test get_analyzer_config with None values in config."""
    config = {
        "analyzer": {
            "analyze_work_patterns": None,
        },
        "work_schedule": {
            "standard_work_hours": None,
            "work_days": None,
        },
    }

    result = cu.get_analyzer_config(config)

    expected = {
        "analyze_work_patterns": None,
        "standard_work_hours": None,
        "work_days": None,
    }

    assert result == expected


@pytest.mark.fast
def test_get_analyzer_config_return_structure() -> None:
    """Test that the function returns the expected dictionary structure."""
    config = {
        "analyzer": {
            "analyze_work_patterns": True,
            "extra_key": "extra_value",
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
            "extra_key": "extra_value",
        },
        "other_section": {
            "some_key": "some_value",
        },
    }

    result = cu.get_analyzer_config(config)

    # Check that result is a dictionary with exactly the expected keys
    assert isinstance(result, dict)
    assert set(result.keys()) == {"analyze_work_patterns", "standard_work_hours", "work_days"}
    assert result["analyze_work_patterns"] is True
    assert result["standard_work_hours"] == 8
    assert result["work_days"] == [0, 1, 2, 3, 4]

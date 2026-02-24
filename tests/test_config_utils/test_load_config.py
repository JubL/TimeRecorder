"""Tests for the config_utils module."""

import pathlib
from unittest.mock import patch

import pytest
import yaml

import src.config_utils as cu


def _write_config(path: pathlib.Path, content: dict | str) -> None:
    """Write config dict or raw string to a YAML file."""
    if isinstance(content, dict):
        path.write_text(yaml.safe_dump(content), encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")


@pytest.mark.fast
def test_load_config_success(tmp_path: pathlib.Path, sample_config: dict, relative_precision: float) -> None:
    """Test successful configuration loading."""
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, sample_config)

    config = cu.load_config(config_path)

    assert config["time_tracking"]["date"] == sample_config["time_tracking"]["date"]
    assert config["time_tracking"]["start_time"] == sample_config["time_tracking"]["start_time"]
    assert config["work_schedule"]["standard_work_hours"] == pytest.approx(
        sample_config["work_schedule"]["standard_work_hours"],
        rel=relative_precision,
    )


@pytest.mark.fast
def test_load_config_file_not_found() -> None:
    """Test configuration loading when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        cu.load_config(pathlib.Path("nonexistent_config.yaml"))


@pytest.mark.fast
def test_load_config_malformed_yaml(tmp_path: pathlib.Path) -> None:
    """Test configuration loading with malformed YAML."""
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, "time_tracking:\n  date: '25.07.2025'\n  start_time: '07:00'\ninvalid: yaml: :")

    with pytest.raises(yaml.YAMLError):
        cu.load_config(config_path)


@pytest.mark.fast
def test_load_config_empty_file(tmp_path: pathlib.Path) -> None:
    """Test configuration loading with empty YAML file."""
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, "")

    config = cu.load_config(config_path)

    assert config is None  # yaml.safe_load returns None for empty files


@pytest.mark.fast
def test_load_config_complex_nested_structure(tmp_path: pathlib.Path, sample_config: dict) -> None:
    """Test configuration loading with complex nested YAML structure."""
    config_data = {
        **sample_config,
        "time_tracking": {
            **sample_config["time_tracking"],
            "nested": {
                "level1": {
                    "level2": {
                        "level3": "deep_value",
                    },
                },
            },
        },
        "logging": {
            **sample_config["logging"],
            "log_path": "timereport_logbook.txt",
            "handlers": ["file", "console"],
            "formatters": {
                "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "simple": "%(levelname)s - %(message)s",
            },
        },
        "work_schedule": {
            **sample_config["work_schedule"],
            "standard_work_hours": 8.5,
            "holidays": {
                "country": "DE",
                "subdivision": "HE",
            },
        },
    }
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, config_data)

    config = cu.load_config(config_path)

    assert config["time_tracking"]["nested"]["level1"]["level2"]["level3"] == "deep_value"
    assert config["logging"]["handlers"] == ["file", "console"]
    assert config["work_schedule"]["standard_work_hours"] == 8.5


@pytest.mark.fast
def test_load_config_with_comments(tmp_path: pathlib.Path) -> None:
    """Test configuration loading with YAML comments."""
    yaml_content = """
# Configuration file for TimeRecorder
time_tracking:
  date: "25.07.2025"  # Current date
  start_time: "07:00"  # Work start time
  end_time: "17:25"    # Work end time
  lunch_break_duration: 60  # Lunch break in minutes
  full_format: "%d.%m.%Y %H:%M:%S"  # Date format

logging:
  log_path: "timereport_logbook.txt"  # Log file path
  log_level: "INFO"  # Logging level

work_schedule:
  standard_work_hours: 8  # Standard work hours per day
  work_days: [0, 1, 2, 3, 4]  # Monday to Friday
  timezone: "Europe/Berlin"  # Timezone
"""
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, yaml_content)

    config = cu.load_config(config_path)

    assert config["time_tracking"]["date"] == "25.07.2025"
    assert config["logging"]["log_level"] == "INFO"
    assert config["work_schedule"]["work_days"] == [0, 1, 2, 3, 4]


@pytest.mark.fast
def test_load_config_with_special_characters(tmp_path: pathlib.Path, sample_config: dict) -> None:
    """Test configuration loading with special characters in values."""
    config_data = {
        **sample_config,
        "time_tracking": {
            **sample_config["time_tracking"],
            "description": "Work time with special chars: äöüß & symbols",
        },
        "logging": {
            **sample_config["logging"],
            "log_path": "timereport_logbook.txt",
            "message": "Log message with quotes: 'single' and \"double\"",
        },
        "work_schedule": {
            **sample_config["work_schedule"],
            "note": "Work schedule with newlines\nand special formatting",
        },
    }
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, config_data)

    config = cu.load_config(config_path)

    assert "äöüß" in config["time_tracking"]["description"]
    assert "'single'" in config["logging"]["message"]
    assert "newlines" in config["work_schedule"]["note"]


@pytest.mark.fast
def test_load_config_file_read_error(tmp_path: pathlib.Path) -> None:
    """Test configuration loading when file read fails."""
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, {"test": "data"})

    with (
        patch("pathlib.Path.open", side_effect=PermissionError("Permission denied")),
        pytest.raises(OSError, match="Permission denied"),
    ):
        cu.load_config(config_path)


@pytest.mark.fast
def test_load_config_yaml_load_error(tmp_path: pathlib.Path) -> None:
    """Test configuration loading when yaml.safe_load fails."""
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, {"test": "data"})

    with patch("yaml.safe_load", side_effect=yaml.YAMLError("YAML parsing error")), pytest.raises(yaml.YAMLError):
        cu.load_config(config_path)


@pytest.mark.fast
def test_load_config_unicode_encoding(tmp_path: pathlib.Path, sample_config: dict) -> None:
    """Test configuration loading with Unicode characters."""
    config_data = {
        **sample_config,
        "time_tracking": {
            **sample_config["time_tracking"],
            "description": "Arbeitszeit mit deutschen Umlauten: äöüß",
            "note": "Work time with emojis: 🕐 📅 ⏰",
        },
    }
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, config_data)

    config = cu.load_config(config_path)

    assert "äöüß" in config["time_tracking"]["description"]
    assert "🕐" in config["time_tracking"]["note"]


@pytest.mark.fast
def test_load_config_return_type(tmp_path: pathlib.Path, sample_config: dict) -> None:
    """Test that load_config returns the correct type."""
    config_data = {
        "time_tracking": {
            "date": sample_config["time_tracking"]["date"],
            "start_time": sample_config["time_tracking"]["start_time"],
        },
    }
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, config_data)

    config = cu.load_config(config_path)

    assert isinstance(config, dict)
    assert isinstance(config["time_tracking"], dict)


@pytest.mark.fast
def test_load_config_with_numeric_types(tmp_path: pathlib.Path, sample_config: dict) -> None:
    """Test configuration loading with various numeric types."""
    config_data = {
        **sample_config,
        "time_tracking": {
            **sample_config["time_tracking"],
            "lunch_break_duration": 60,
            "overtime_hours": 2.5,
            "work_days_count": 5,
        },
    }
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, config_data)

    config = cu.load_config(config_path)

    assert isinstance(config["time_tracking"]["lunch_break_duration"], int)
    assert isinstance(config["time_tracking"]["overtime_hours"], float)
    assert isinstance(config["time_tracking"]["work_days_count"], int)
    assert config["time_tracking"]["lunch_break_duration"] == 60
    assert config["time_tracking"]["overtime_hours"] == 2.5

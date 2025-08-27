"""Tests for the config_utils module."""

import pathlib
import tempfile
from unittest.mock import patch

import pytest
import yaml

import src.config_utils as cu


@pytest.mark.fast
def test_load_config_success(relative_precision: float) -> None:
    """Test successful configuration loading."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        config_data = {
            "time_tracking": {
                "use_boot_time": True,
                "date": "25.07.2025",
                "start_time": "07:00",
                "end_time": "17:25",
                "lunch_break_duration": 60,
                "full_format": "%d.%m.%Y %H:%M:%S",
            },
            "logging": {
                "enabled": False,
                "log_path": "timereport_logbook.txt",
                "log_level": "INFO",
            },
            "work_schedule": {
                "standard_work_hours": 8,
                "work_days": [0, 1, 2, 3, 4],
                "timezone": "Europe/Berlin",
            },
        }
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert config["time_tracking"]["date"] == "25.07.2025"
        assert config["logging"]["enabled"] is False
        assert config["work_schedule"]["standard_work_hours"] == pytest.approx(8, rel=relative_precision)
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_file_not_found() -> None:
    """Test configuration loading when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        cu.load_config(pathlib.Path("nonexistent_config.yaml"))


@pytest.mark.fast
def test_load_config_malformed_yaml() -> None:
    """Test configuration loading with malformed YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        # Write malformed YAML
        f.write("time_tracking:\n  date: '25.07.2025'\n  start_time: '07:00'\ninvalid: yaml: :")
        config_path = f.name

    try:
        with pytest.raises(yaml.YAMLError):
            cu.load_config(pathlib.Path(config_path))
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_empty_file() -> None:
    """Test configuration loading with empty YAML file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        # Write empty file
        f.write("")
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert config is None  # yaml.safe_load returns None for empty files
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_complex_nested_structure() -> None:
    """Test configuration loading with complex nested YAML structure."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        config_data = {
            "time_tracking": {
                "date": "25.07.2025",
                "start_time": "07:00",
                "end_time": "17:25",
                "lunch_break_duration": 60,
                "full_format": "%d.%m.%Y %H:%M:%S",
                "nested": {
                    "level1": {
                        "level2": {
                            "level3": "deep_value",
                        },
                    },
                },
            },
            "logging": {
                "log_path": "timereport_logbook.txt",
                "log_level": "INFO",
                "handlers": ["file", "console"],
                "formatters": {
                    "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "simple": "%(levelname)s - %(message)s",
                },
            },
            "work_schedule": {
                "standard_work_hours": 8.5,
                "work_days": [0, 1, 2, 3, 4],
                "timezone": "Europe/Berlin",
                "holidays": {
                    "country": "DE",
                    "subdivision": "HE",
                },
            },
        }
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert config["time_tracking"]["nested"]["level1"]["level2"]["level3"] == "deep_value"
        assert config["logging"]["handlers"] == ["file", "console"]
        assert config["work_schedule"]["standard_work_hours"] == 8.5
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_with_comments() -> None:
    """Test configuration loading with YAML comments."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
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
        f.write(yaml_content)
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert config["time_tracking"]["date"] == "25.07.2025"
        assert config["logging"]["log_level"] == "INFO"
        assert config["work_schedule"]["work_days"] == [0, 1, 2, 3, 4]
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_with_special_characters() -> None:
    """Test configuration loading with special characters in values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        config_data = {
            "time_tracking": {
                "date": "25.07.2025",
                "start_time": "07:00",
                "end_time": "17:25",
                "full_format": "%d.%m.%Y %H:%M:%S",
                "description": "Work time with special chars: äöüß & symbols",
            },
            "logging": {
                "log_path": "timereport_logbook.txt",
                "log_level": "INFO",
                "message": "Log message with quotes: 'single' and \"double\"",
            },
            "work_schedule": {
                "standard_work_hours": 8,
                "work_days": [0, 1, 2, 3, 4],
                "timezone": "Europe/Berlin",
                "note": "Work schedule with newlines\nand special formatting",
            },
        }
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert "äöüß" in config["time_tracking"]["description"]
        assert "'single'" in config["logging"]["message"]
        assert "newlines" in config["work_schedule"]["note"]
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_file_read_error() -> None:
    """Test configuration loading when file read fails."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        config_data = {"test": "data"}
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        # Mock the pathlib.Path.open method to raise an exception
        with (
            patch("pathlib.Path.open", side_effect=PermissionError("Permission denied")),
            pytest.raises(OSError, match="Permission denied"),
        ):
            cu.load_config(pathlib.Path(config_path))
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_yaml_load_error() -> None:
    """Test configuration loading when yaml.safe_load fails."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        config_data = {"test": "data"}
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        # Mock yaml.safe_load to raise an exception
        with patch("yaml.safe_load", side_effect=yaml.YAMLError("YAML parsing error")), pytest.raises(yaml.YAMLError):
            cu.load_config(pathlib.Path(config_path))
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_unicode_encoding() -> None:
    """Test configuration loading with Unicode characters."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        config_data = {
            "time_tracking": {
                "date": "25.07.2025",
                "description": "Arbeitszeit mit deutschen Umlauten: äöüß",
                "note": "Work time with emojis: 🕐 📅 ⏰",
            },
            "logging": {
                "log_path": "timereport_logbook.txt",
                "log_level": "INFO",
            },
        }
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert "äöüß" in config["time_tracking"]["description"]
        assert "🕐" in config["time_tracking"]["note"]
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_return_type() -> None:
    """Test that load_config returns the correct type."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        config_data = {
            "time_tracking": {
                "date": "25.07.2025",
                "start_time": "07:00",
            },
        }
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert isinstance(config, dict)
        assert isinstance(config["time_tracking"], dict)
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_with_numeric_types() -> None:
    """Test configuration loading with various numeric types."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        config_data = {
            "time_tracking": {
                "date": "25.07.2025",
                "start_time": "07:00",
                "lunch_break_duration": 60,  # integer
                "overtime_hours": 2.5,  # float
                "work_days_count": 5,  # integer
            },
            "logging": {
                "log_path": "timereport_logbook.txt",
                "log_level": "INFO",
            },
        }
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert isinstance(config["time_tracking"]["lunch_break_duration"], int)
        assert isinstance(config["time_tracking"]["overtime_hours"], float)
        assert isinstance(config["time_tracking"]["work_days_count"], int)
        assert config["time_tracking"]["lunch_break_duration"] == 60
        assert config["time_tracking"]["overtime_hours"] == 2.5
    finally:
        pathlib.Path(config_path).unlink()

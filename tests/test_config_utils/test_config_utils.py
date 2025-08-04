"""Tests for the config_utils module."""

import pathlib
import tempfile
from unittest.mock import Mock, patch

import pytest
import yaml

import src.config_utils as cu


@pytest.mark.fast
def test_load_config_success() -> None:
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
        yaml.dump(config_data, f)
        config_path = f.name

    try:
        config = cu.load_config(pathlib.Path(config_path))
        assert config["time_tracking"]["date"] == "25.07.2025"
        assert config["logging"]["enabled"] is False
        assert config["work_schedule"]["standard_work_hours"] == pytest.approx(8, rel=pytest.RELATIVE_PRECISION)
    finally:
        pathlib.Path(config_path).unlink()


@pytest.mark.fast
def test_load_config_file_not_found() -> None:
    """Test configuration loading when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        cu.load_config(pathlib.Path("nonexistent_config.yaml"))


@pytest.mark.fast
def test_get_time_recorder_config() -> None:
    """Test extraction of TimeRecorder configuration."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:25",
            "lunch_break_duration": 60,
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    }

    result = cu.get_time_recorder_config(config)

    assert result["date"] == "25.07.2025"
    assert result["start_time"] == "07:00"
    assert result["end_time"] == "17:25"
    assert result["lunch_break_duration"] == pytest.approx(60, rel=pytest.RELATIVE_PRECISION)
    assert result["full_format"] == "%d.%m.%Y %H:%M:%S"


@pytest.mark.fast
def test_get_time_recorder_config_with_defaults() -> None:
    """Test TimeRecorder configuration with missing values."""
    config: dict = {"time_tracking": {}}

    result = cu.get_time_recorder_config(config)

    assert result["date"] == "01.08.2025"
    assert result["start_time"] == "07:00"
    assert result["end_time"] == "17:25"
    assert result["lunch_break_duration"] == pytest.approx(60, rel=pytest.RELATIVE_PRECISION)


@pytest.mark.fast
def test_get_logbook_config() -> None:
    """Test extraction of Logbook configuration."""
    config: dict = {
        "logging": {
            "log_path": "test_logbook.txt",
        },
        "time_tracking": {
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
    }

    result = cu.get_logbook_config(config)

    assert result["log_path"] == pathlib.Path.cwd() / "test_logbook.txt"
    assert result["full_format"] == "%d.%m.%Y %H:%M:%S"


@pytest.mark.fast
def test_get_processing_config() -> None:
    """Test extraction of processing configuration."""
    config: dict = {
        "time_tracking": {
            "use_boot_time": True,
        },
        "logging": {
            "enabled": True,
        },
        "data_processing": {
            "auto_squash": True,
            "add_missing_days": True,
            "calculate_weekly_hours": True,
        },
    }

    result = cu.get_processing_config(config)

    assert result["use_boot_time"] is True
    assert result["log_enabled"] is True
    assert result["auto_squash"] is True
    assert result["add_missing_days"] is True
    assert result["calculate_weekly_hours"] is True


@pytest.mark.fast
def test_validate_config_success() -> None:
    """Test successful configuration validation."""
    config: dict = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:25",
            "lunch_break_duration": 60,
        },
        "logging": {
            "log_path": "timereport_logbook.txt",
        },
        "work_schedule": {
            "standard_work_hours": 8,
        },
    }

    assert cu.validate_config(config) is True


@pytest.mark.fast
def test_validate_config_missing_section() -> None:
    """Test configuration validation with missing required section."""
    config: dict = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:25",
            "lunch_break_duration": 60,
        },
        # Missing 'logging' and 'work_schedule' sections
    }

    assert cu.validate_config(config) is False


@pytest.mark.fast
def test_validate_config_missing_field() -> None:
    """Test configuration validation with missing required field."""
    config: dict = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            # Missing 'end_time' and 'lunch_break_duration'
        },
        "logging": {
            "log_path": "timereport_logbook.txt",
        },
        "work_schedule": {
            "standard_work_hours": 8,
        },
    }

    assert cu.validate_config(config) is False


@patch("pathlib.Path.exists")
@patch("pathlib.Path.open")
@patch("yaml.dump")
@pytest.mark.fast
def test_create_default_config_new_file(mock_yaml_dump: Mock, mock_open: Mock, mock_exists: Mock) -> None:
    """Test creating default configuration file when it doesn't exist."""
    mock_exists.return_value = False
    mock_file = Mock()
    mock_open.return_value.__enter__.return_value = mock_file

    cu.create_default_config(pathlib.Path("test_config.yaml"))

    mock_open.assert_called_once()
    mock_yaml_dump.assert_called_once()


@patch("pathlib.Path.exists")
@pytest.mark.fast
def test_create_default_config_existing_file(mock_exists: Mock) -> None:
    """Test creating default configuration when file already exists."""
    mock_exists.return_value = True

    # Should not raise any exception
    cu.create_default_config(pathlib.Path("test_config.yaml"))

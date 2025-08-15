"""Tests for the config_utils module."""

import pathlib
import tempfile

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

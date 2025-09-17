"""Fixtures for the unit tests."""

import matplotlib as mpl

mpl.use("Agg")  # Use non-interactive backend to suppress window creation

import pathlib
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

import src.logbook as lb
import src.time_recorder as tr


@pytest.fixture
def relative_precision() -> float:
    """Fixture to provide a relative precision for pytest."""
    return 1e-12


@pytest.fixture
def fake_boot_timestamp() -> float:
    """Fixture to provide a fake boot timestamp."""
    return datetime(2025, 4, 25, 6, 30, 0, tzinfo=ZoneInfo("Europe/Berlin")).timestamp()


@pytest.fixture
def fake_boot_timestamp_with_timezone() -> float:
    """Fixture to provide a fake boot timestamp with timezone."""
    return datetime(2025, 4, 25, 6, 30, 0, tzinfo=ZoneInfo("Europe/Berlin")).timestamp()


@pytest.fixture
def line() -> tr.TimeRecorder:
    """Fixture to create a sample TimeRecorder for calculate_overtime tests."""
    return tr.TimeRecorder(
        {
            "date": "24.04.2025",
            "start_time": "08:00",
            "end_time": "16:00",
            "end_now": False,
            "lunch_break_duration": 0,
            "timezone": "Europe/Berlin",
            "full_format": "%d.%m.%Y %H:%M:%S",
            "standard_work_hours": 8,
        },
    )


@pytest.fixture
def logbook(tmp_path: pathlib.Path) -> lb.Logbook:
    """Fixture to create a sample Logbook for testing with isolated temporary file."""
    # Use pytest's tmp_path fixture for automatic test isolation and cleanup
    log_file = tmp_path / "log.csv"

    return lb.Logbook(
        data={
            "log_path": log_file,
            "full_format": "%d.%m.%Y %H:%M:%S",
            "holidays": "DE",
            "subdivision": "HE",
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
        },
    )


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Fixture to create a sample DataFrame with multiple entries for the same date."""
    return pd.DataFrame(
        {
            "weekday": ["Mon", "Mon", "Mon", "Tue", "Tue"],
            "date": ["24.04.2025", "24.04.2025", "24.04.2025", "25.04.2025", "25.04.2025"],
            "start_time": ["08:00:00", "11:30:00", "14:00:00", "08:00:00", "13:00:00"],
            "end_time": ["10:00:00", "13:00:00", "17:00:00", "12:00:00", "17:00:00"],
            "lunch_break_duration": [30, 45, 60, 60, 30],
            "work_time": [1.5, 1.25, 3.0, 4.0, 4.0],
            "case": ["undertime", "undertime", "undertime", "undertime", "undertime"],
            "overtime": [-6.5, -6.75, -5.0, -4.0, -4.0],
        },
    )


@pytest.fixture
def sample_logbook_df() -> pd.DataFrame:
    """Sample logbook data for testing."""
    return pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "05.01.2024"],
            "start_time": ["08:00:00", "07:30:00", "08:15:00", "07:45:00", "08:00:00"],
            "end_time": ["17:00:00", "16:30:00", "17:15:00", "16:45:00", "17:00:00"],
            "lunch_break_duration": [60, 60, 60, 60, 60],
            "work_time": [7.0, 7.0, 7.0, 7.0, 7.0],
            "case": ["overtime", "overtime", "overtime", "overtime", "overtime"],
            "overtime": [0.0, 0.0, 0.0, 0.0, 0.0],
        },
    )


@pytest.fixture
def sample_config() -> dict:
    """Sample configuration dictionary for testing."""
    return {
        "time_tracking": {
            "date": "01.08.2025",
            "start_time": "07:30",
            "end_time": "17:25",
            "lunch_break_duration": 60,
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
        "logging": {
            "log_path": "timereport_logbook.csv",
            "log_level": "INFO",
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
            "timezone": "Europe/Berlin",
        },
        "holidays": {
            "country": "DE",
            "subdivision": "HE",
        },
        "data_processing": {
            "use_boot_time": True,
            "logging_enabled": False,
            "auto_squash": True,
            "add_missing_days": True,
        },
        "display": {
            "show_tail": 4,
        },
        "visualization": {
            "color_scheme": "ocean",
            "num_months": 13,
            "plot": True,
        },
        "analyzer": {
            "analyze_work_patterns": True,
        },
    }

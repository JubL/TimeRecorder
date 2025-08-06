"""Fixtures for the unit tests."""

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
    return 1e-12  # TODO: make this a parameter


@pytest.fixture
def fake_boot_timestamp() -> float:
    """Fixture to provide a fake boot timestamp."""
    return datetime(2025, 4, 25, 6, 30, 0).timestamp()


@pytest.fixture
def fake_boot_timestamp_with_timezone() -> float:
    """Fixture to provide a fake boot timestamp with timezone."""
    return datetime(2025, 4, 25, 6, 30, 0, tzinfo=ZoneInfo("Europe/Berlin")).timestamp()


@pytest.fixture
def line() -> tr.TimeRecorder:
    """Fixture to create a sample TimeRecorder for calculate_overtime tests."""
    return tr.TimeRecorder(
        date="24.04.2025",
        start_time="08:00",
        end_time="16:00",
        lunch_break_duration=0,
        timezone="Europe/Berlin",
    )


@pytest.fixture
def logbook(tmp_path: pathlib.Path) -> lb.Logbook:
    """Fixture to create a sample Logbook for testing."""
    return lb.Logbook(log_path=tmp_path / "log.csv")


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
            "lunch_break_duration": ["1.0", "1.0", "1.0", "1.0", "1.0"],
            "work_time": ["7.0", "7.0", "7.0", "7.0", "7.0"],
            "case": ["overtime", "overtime", "overtime", "overtime", "overtime"],
            "overtime": ["0.0", "0.0", "0.0", "0.0", "0.0"],
        },
    )

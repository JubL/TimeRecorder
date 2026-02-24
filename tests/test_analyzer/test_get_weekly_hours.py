"""Unit tests for the Analyzer get_weekly_hours_from_log method."""

import logging

import pandas as pd
import pytest

from src import analyzer


@pytest.mark.fast
def test_get_weekly_hours_basic(analyzer_instance: analyzer.Analyzer, relative_precision: float) -> None:
    """Test get_weekly_hours_from_log with sample data."""
    weekly, daily = analyzer_instance.get_weekly_hours_from_log()

    assert isinstance(weekly, float)
    assert isinstance(daily, float)
    # sample_logbook_df: 5 days, 7h each, work_days=5 -> weekly = 7*5 = 35, daily overtime = 0
    assert weekly == pytest.approx(35.0, rel=relative_precision)
    assert daily == pytest.approx(0.0, rel=relative_precision)


@pytest.mark.fast
def test_get_weekly_hours_with_overtime(
    analyzer_data: dict,
    relative_precision: float,
) -> None:
    """Test get_weekly_hours_from_log with overtime values."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "work_time": [8.0, 8.0, 8.0],
            "overtime": [1.0, 2.0, 0.0],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)
    weekly, daily = ana.get_weekly_hours_from_log()

    assert weekly == pytest.approx(40.0, rel=relative_precision)  # 8*5 work days
    assert daily == pytest.approx(1.0, rel=relative_precision)  # (1+2+0)/3 = 1.0


@pytest.mark.fast
def test_get_weekly_hours_no_work_days(
    analyzer_data: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test get_weekly_hours_from_log returns 0 when no work days."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "work_time": [0.0, 0.0],
            "overtime": [0.0, 0.0],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)

    with caplog.at_level(logging.WARNING, logger="src.analyzer"):
        weekly, daily = ana.get_weekly_hours_from_log()

    assert weekly == 0.0
    assert daily == 0.0
    assert "No work days" in caplog.text


@pytest.mark.fast
def test_get_weekly_hours_non_numeric_work_time_returns_zero(
    analyzer_data: dict,
) -> None:
    """Test get_weekly_hours_from_log returns 0 on conversion error."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "work_time": ["invalid", "also_invalid"],
            "overtime": [0.0, 0.0],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)
    weekly, daily = ana.get_weekly_hours_from_log()

    assert weekly == 0.0
    assert daily == 0.0


@pytest.mark.fast
def test_get_weekly_hours_custom_work_days(
    analyzer_data: dict,
    relative_precision: float,
) -> None:
    """Test get_weekly_hours_from_log with custom work week."""
    analyzer_data["work_days"] = [0, 1, 2]  # 3 days per week
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "work_time": [8.0, 8.0],
            "overtime": [0.0, 0.0],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)
    weekly, daily = ana.get_weekly_hours_from_log()

    # 2 days * 8h = 16h total, avg = 8h/day, weekly = 8 * 3 = 24
    assert weekly == pytest.approx(24.0, rel=relative_precision)
    assert daily == pytest.approx(0.0, rel=relative_precision)


@pytest.mark.fast
def test_get_weekly_hours_partial_work_days(
    analyzer_data: dict,
    relative_precision: float,
) -> None:
    """Test get_weekly_hours_from_log with some zero work_time days."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "work_time": [8.0, 0.0, 8.0],
            "overtime": [0.5, 0.0, 0.5],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)
    weekly, daily = ana.get_weekly_hours_from_log()

    # num_days with work_time > 0 = 2
    # weekly_hours = (8+8)/2 * 5 = 40
    # daily_overtime = (0.5+0.5)/2 = 0.5
    assert weekly == pytest.approx(40.0, rel=relative_precision)
    assert daily == pytest.approx(0.5, rel=relative_precision)

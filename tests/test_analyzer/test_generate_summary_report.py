"""Unit tests for the Analyzer generate_summary_report method."""

import logging

import pandas as pd
import pytest

from src import analyzer


@pytest.mark.fast
def test_generate_summary_report_runs_without_error(
    analyzer_instance: analyzer.Analyzer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test generate_summary_report runs and logs output."""
    with caplog.at_level(logging.INFO, logger="src.analyzer"):
        analyzer_instance.generate_summary_report()

    assert "Analytics" in caplog.text
    assert "Standard Hours" in caplog.text or "Average Weekly" in caplog.text


@pytest.mark.fast
def test_generate_summary_report_with_valid_data(
    analyzer_data: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test generate_summary_report content with valid overtime data."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "work_time": [8.0, 8.0, 8.0],
            "overtime": [1.0, 0.0, -0.5],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)

    with caplog.at_level(logging.INFO, logger="src.analyzer"):
        ana.generate_summary_report()

    assert "Mean overtime" in caplog.text
    assert "Outliers" in caplog.text


@pytest.mark.fast
def test_generate_summary_report_with_no_valid_overtime(
    analyzer_data: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test generate_summary_report when all overtime is NaN."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "work_time": [8.0, 8.0],
            "overtime": [float("nan"), float("nan")],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)

    with caplog.at_level(logging.INFO, logger="src.analyzer"):
        ana.generate_summary_report()

    assert "No valid data available" in caplog.text

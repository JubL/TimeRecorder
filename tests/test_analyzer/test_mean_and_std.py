"""Unit tests for the Analyzer mean_and_std method."""

import logging

import pandas as pd
import pytest

from src import analyzer


@pytest.mark.fast
def test_mean_and_std_with_valid_data(analyzer_instance: analyzer.Analyzer) -> None:
    """Test mean_and_std with valid overtime data."""
    mean, std = analyzer_instance.mean_and_std()

    assert mean is not None
    assert std is not None
    assert mean == 0.0  # sample_logbook_df has all overtime 0.0
    assert std == 0.0


@pytest.mark.fast
def test_mean_and_std_with_varied_overtime(
    analyzer_data: dict,
) -> None:
    """Test mean_and_std with varied overtime values."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "work_time": [8.0, 8.0, 8.0],
            "overtime": [1.0, 2.0, 3.0],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)
    mean, std = ana.mean_and_std()

    assert mean == pytest.approx(2.0, rel=1e-6)
    assert std == pytest.approx(1.0, rel=1e-6)


@pytest.mark.fast
def test_mean_and_std_with_all_nan_returns_none(
    analyzer_data: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test mean_and_std returns (None, None) when all overtime is NaN."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "work_time": [8.0, 8.0],
            "overtime": [float("nan"), float("nan")],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)

    with caplog.at_level(logging.WARNING, logger="src.analyzer"):
        mean, std = ana.mean_and_std()

    assert mean is None
    assert std is None
    assert "No valid overtime" in caplog.text or "valid" in caplog.text.lower()


@pytest.mark.fast
def test_mean_and_std_with_mixed_valid_and_nan(
    analyzer_data: dict,
) -> None:
    """Test mean_and_std excludes NaN and computes from valid values only."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "work_time": [8.0, 8.0, 8.0],
            "overtime": [1.0, float("nan"), 3.0],
        },
    )
    ana = analyzer.Analyzer(analyzer_data, df)
    mean, std = ana.mean_and_std()

    assert mean == pytest.approx(2.0, rel=1e-6)  # (1 + 3) / 2
    assert std is not None

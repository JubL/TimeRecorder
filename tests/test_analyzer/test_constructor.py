"""Unit tests for the Analyzer constructor."""

import pandas as pd
import pytest

from src import analyzer


@pytest.mark.fast
def test_constructor_basic_initialization(
    analyzer_data: dict,
    sample_logbook_df: pd.DataFrame,
) -> None:
    """Test basic Analyzer initialization."""
    ana = analyzer.Analyzer(analyzer_data, sample_logbook_df)

    assert ana.logbook_df is not None
    assert len(ana.logbook_df) == len(sample_logbook_df)
    assert ana.standard_work_hours == 8
    assert ana.work_days == [0, 1, 2, 3, 4]
    assert ana.outlier_method == "iqr"
    assert ana.outlier_threshold == 1.5
    assert ana.sec_in_min == 60
    assert ana.sec_in_hour == 3600
    assert ana.min_in_hour == 60


@pytest.mark.fast
def test_constructor_empty_dataframe_raises(analyzer_data: dict) -> None:
    """Test that empty DataFrame raises ValueError."""
    df = pd.DataFrame(columns=["date", "work_time", "overtime"])

    with pytest.raises(ValueError, match="logbook_df cannot be empty"):
        analyzer.Analyzer(analyzer_data, df)


@pytest.mark.fast
def test_constructor_not_dataframe_raises(analyzer_data: dict) -> None:
    """Test that non-DataFrame raises TypeError."""
    with pytest.raises(TypeError, match="logbook_df must be a pandas DataFrame"):
        analyzer.Analyzer(analyzer_data, [])  # type: ignore[arg-type]


@pytest.mark.fast
def test_constructor_missing_overtime_column_raises(analyzer_data: dict) -> None:
    """Test that missing overtime column raises KeyError (constructor requires it)."""
    df = pd.DataFrame(
        {"date": ["01.01.2024"], "work_time": [8.0]},
    )

    with pytest.raises(KeyError, match="overtime"):
        analyzer.Analyzer(analyzer_data, df)


@pytest.mark.fast
def test_constructor_does_not_mutate_input(
    analyzer_data: dict,
    sample_logbook_df: pd.DataFrame,
) -> None:
    """Test that constructor does not mutate the input DataFrame."""
    original_len = len(sample_logbook_df)
    ana = analyzer.Analyzer(analyzer_data, sample_logbook_df)

    # Call method that might mutate (e.g. detect_outliers_isolation_forest adds column)
    ana.detect_outliers(method="iqr", threshold=1.5)

    assert len(sample_logbook_df) == original_len
    assert "anomaly_score" not in sample_logbook_df.columns

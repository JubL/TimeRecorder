import pandas as pd
import pytest

import src.logbook as lb


@pytest.mark.fast
def test_remove_duplicate_lines_empty_dataframe(logbook: lb.Logbook) -> None:
    """Test that remove_duplicate_lines returns empty DataFrame when input is empty."""
    empty_df = pd.DataFrame()
    result = logbook.remove_duplicate_lines(empty_df)
    assert result.empty
    assert isinstance(result, pd.DataFrame)


@pytest.mark.fast
def test_remove_duplicate_lines_no_duplicates(logbook: lb.Logbook) -> None:
    """Test that remove_duplicate_lines returns unchanged DataFrame when no duplicates exist."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["24.04.2025", "25.04.2025", "26.04.2025"],
            "start_time": ["08:00:00", "09:00:00", "08:30:00"],
            "end_time": ["17:00:00", "18:00:00", "17:30:00"],
            "lunch_break_duration": [60, 45, 60],
            "work_time": [8.0, 8.25, 8.0],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": [0.0, 0.25, 0.0],
        },
    )

    result = logbook.remove_duplicate_lines(df)
    pd.testing.assert_frame_equal(result, df)


@pytest.mark.fast
def test_remove_duplicate_lines_exact_duplicates(logbook: lb.Logbook) -> None:
    """Test that remove_duplicate_lines removes exact duplicates and keeps first occurrence."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon", "Tue", "Tue", "Wed"],
            "date": ["24.04.2025", "24.04.2025", "25.04.2025", "25.04.2025", "26.04.2025"],
            "start_time": ["08:00:00", "08:00:00", "09:00:00", "09:00:00", "08:30:00"],
            "end_time": ["17:00:00", "17:00:00", "18:00:00", "18:00:00", "17:30:00"],
            "lunch_break_duration": [30, 30, 45, 45, 60],
            "work_time": [8.5, 8.5, 8.25, 8.25, 8.0],
            "case": ["overtime", "overtime", "overtime", "overtime", "undertime"],
            "overtime": [0.5, 0.5, 0.25, 0.25, -1.0],
        },
    )

    result = logbook.remove_duplicate_lines(df)

    # Should have 3 rows (one from each unique set)
    assert len(result) == 3

    # Check that first occurrence of each duplicate is kept
    # Note: The method preserves original indices, so we need to reset them for comparison
    expected_df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["24.04.2025", "25.04.2025", "26.04.2025"],
            "start_time": ["08:00:00", "09:00:00", "08:30:00"],
            "end_time": ["17:00:00", "18:00:00", "17:30:00"],
            "lunch_break_duration": [30, 45, 60],
            "work_time": [8.5, 8.25, 8.0],
            "case": ["overtime", "overtime", "undertime"],
            "overtime": [0.5, 0.25, -1.0],
        },
    )

    # Reset indices for comparison
    result_reset = result.reset_index(drop=True)
    pd.testing.assert_frame_equal(result_reset, expected_df)


@pytest.mark.fast
def test_remove_duplicate_lines_multiple_duplicate_sets(logbook: lb.Logbook) -> None:
    """Test that remove_duplicate_lines handles multiple sets of duplicates correctly."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon", "Mon", "Tue", "Tue", "Wed", "Wed", "Wed"],
            "date": ["24.04.2025", "24.04.2025", "24.04.2025", "25.04.2025", "25.04.2025", "26.04.2025", "26.04.2025", "26.04.2025"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00", "09:00:00", "09:00:00", "08:30:00", "08:30:00", "08:30:00"],
            "end_time": ["17:00:00", "17:00:00", "17:00:00", "18:00:00", "18:00:00", "17:30:00", "17:30:00", "17:30:00"],
            "lunch_break_duration": [30, 30, 30, 45, 45, 60, 60, 60],
            "work_time": [8.5, 8.5, 8.5, 8.25, 8.25, 8.0, 8.0, 8.0],
            "case": ["overtime", "overtime", "overtime", "overtime", "overtime", "undertime", "undertime", "undertime"],
            "overtime": [0.5, 0.5, 0.5, 0.25, 0.25, -1.0, -1.0, -1.0],
        },
    )

    result = logbook.remove_duplicate_lines(df)

    # Should have 3 rows (one from each unique set)
    assert len(result) == 3

    # Check that first occurrence of each duplicate is kept
    expected_df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["24.04.2025", "25.04.2025", "26.04.2025"],
            "start_time": ["08:00:00", "09:00:00", "08:30:00"],
            "end_time": ["17:00:00", "18:00:00", "17:30:00"],
            "lunch_break_duration": [30, 45, 60],
            "work_time": [8.5, 8.25, 8.0],
            "case": ["overtime", "overtime", "undertime"],
            "overtime": [0.5, 0.25, -1.0],
        },
    )

    # Reset indices for comparison
    result_reset = result.reset_index(drop=True)
    pd.testing.assert_frame_equal(result_reset, expected_df)


@pytest.mark.fast
def test_remove_duplicate_lines_partial_duplicates_not_removed(logbook: lb.Logbook) -> None:
    """Test that remove_duplicate_lines only removes exact duplicates, not partial matches."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon", "Tue"],
            "date": ["24.04.2025", "24.04.2025", "25.04.2025"],
            "start_time": ["08:00:00", "08:00:00", "09:00:00"],
            "end_time": ["17:00:00", "17:00:00", "18:00:00"],
            "lunch_break_duration": [30, 45, 60],  # Different values
            "work_time": [8.5, 8.5, 8.25],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": [0.5, 0.5, 0.25],
        },
    )

    result = logbook.remove_duplicate_lines(df)

    # Should have 3 rows (no exact duplicates due to different lunch_break_duration)
    assert len(result) == 3

    # Reset indices for comparison
    result_reset = result.reset_index(drop=True)
    pd.testing.assert_frame_equal(result_reset, df)


@pytest.mark.fast
def test_remove_duplicate_lines_preserves_column_order(logbook: lb.Logbook) -> None:
    """Test that remove_duplicate_lines preserves the original column order."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon"],
            "date": ["24.04.2025", "24.04.2025"],
            "start_time": ["08:00:00", "08:00:00"],
            "end_time": ["17:00:00", "17:00:00"],
            "lunch_break_duration": [30, 30],
            "work_time": [8.5, 8.5],
            "case": ["overtime", "overtime"],
            "overtime": [0.5, 0.5],
        },
    )

    original_columns = list(df.columns)
    result = logbook.remove_duplicate_lines(df)

    assert list(result.columns) == original_columns


@pytest.mark.fast
def test_remove_duplicate_lines_with_nan_values(logbook: lb.Logbook) -> None:
    """Test that remove_duplicate_lines handles NaN values correctly."""
    df = pd.DataFrame(
        {
            "weekday": ["Mon", "Mon", "Tue"],
            "date": ["24.04.2025", "24.04.2025", "25.04.2025"],
            "start_time": ["08:00:00", "08:00:00", "09:00:00"],
            "end_time": ["17:00:00", "17:00:00", "18:00:00"],
            "lunch_break_duration": [30, 30, 60],
            "work_time": [8.5, 8.5, 8.25],
            "case": ["overtime", "overtime", "overtime"],
            "overtime": [0.5, 0.5, 0.25],
        },
    )

    # Add some NaN values
    df.loc[0, "lunch_break_duration"] = pd.NA
    df.loc[1, "lunch_break_duration"] = pd.NA

    result = logbook.remove_duplicate_lines(df)

    # Should have 2 rows (first two are exact duplicates including NaN)
    assert len(result) == 2

    # Check that NaN values are handled correctly
    # Use pd.isna() for proper NaN comparison
    assert pd.isna(result.iloc[0]["lunch_break_duration"])
    assert result.iloc[1]["lunch_break_duration"] == 60

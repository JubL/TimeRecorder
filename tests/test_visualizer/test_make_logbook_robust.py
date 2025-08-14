"""Unit tests for the Visualizer make_logbook_robust method."""

import pandas as pd
import pytest

import src.visualizer as viz


@pytest.mark.fast
def test_make_logbook_robust_basic_conversion() -> None:
    """Test basic data type conversion and cleaning."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "work_time": ["8.0", "7.5"],
            "overtime": ["0.0", "0.5"],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    # Check that date column is converted to datetime
    assert pd.api.types.is_datetime64_any_dtype(visualizer.df["date"])

    # Check that work_time and overtime are converted to numeric
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # Check values
    assert visualizer.df["work_time"].iloc[0] == 8.0
    assert visualizer.df["work_time"].iloc[1] == 7.5
    assert visualizer.df["overtime"].iloc[0] == 0.0
    assert visualizer.df["overtime"].iloc[1] == 0.5


@pytest.mark.fast
def test_make_logbook_robust_handle_missing_values() -> None:
    """Test handling of missing values in work_time and overtime."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024"],
            "work_time": ["8.0", "", "7.5", ""],
            "overtime": ["0.0", "1.0", "", ""],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    # Missing values should be filled with 0.0
    assert visualizer.df["work_time"].iloc[1] == 0.0
    assert visualizer.df["overtime"].iloc[2] == 0.0


@pytest.mark.fast
def test_make_logbook_robust_handle_invalid_numeric() -> None:
    """Test handling of invalid numeric values."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "work_time": ["8.0", "invalid"],
            "overtime": ["0.0", "not_a_number"],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    # Invalid values should be converted to NaN and then filled with 0.0
    assert visualizer.df["work_time"].iloc[1] == 0.0
    assert visualizer.df["overtime"].iloc[1] == 0.0


@pytest.mark.fast
def test_make_logbook_robust_negative_overtime_handling() -> None:
    """Test that negative overtime values are set to 0.0."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "work_time": ["8.0", "7.0", "9.0"],
            "overtime": ["0.0", "-1.0", "1.0"],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    # Negative overtime should be set to 0.0
    assert visualizer.df["overtime"].iloc[0] == 0.0
    assert visualizer.df["overtime"].iloc[1] == 0.0  # Was -1.0
    assert visualizer.df["overtime"].iloc[2] == 1.0  # Positive value unchanged


@pytest.mark.fast
def test_make_logbook_robust_date_format_parsing() -> None:
    """Test date format parsing with different formats."""
    # Test with different date formats
    test_cases = [  # use parametrize fixture instead
        ("%d.%m.%Y", "01.01.2024"),
        ("%Y-%m-%d", "2024-01-01"),
        ("%m/%d/%Y", "01/01/2024"),
    ]

    for date_format, date_str in test_cases:
        full_format = f"{date_format} %H:%M:%S"
        df = pd.DataFrame(
            {
                "date": [date_str],
                "work_time": ["8.0"],
                "overtime": ["0.0"],
            },
        )

        data = {
            "full_format": full_format,
            "color_scheme": "ocean",
            "num_months": 12,
            "standard_work_hours": 8.0,
            "work_days": [0, 1, 2, 3, 4],
        }

        visualizer = viz.Visualizer(df, data)

        # Date should be successfully converted to datetime
        assert pd.api.types.is_datetime64_any_dtype(visualizer.df["date"])
        assert not visualizer.df["date"].isna().any()


@pytest.mark.fast
def test_make_logbook_robust_mixed_data_types() -> None:
    """Test handling of mixed data types in numeric columns."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "work_time": [8.0, "7.5", 9],
            "overtime": [0.0, -1.5, "2.0"],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    # All values should be converted to float
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # Check specific values
    assert visualizer.df["work_time"].iloc[0] == 8.0
    assert visualizer.df["work_time"].iloc[1] == 7.5
    assert visualizer.df["work_time"].iloc[2] == 9.0
    assert visualizer.df["overtime"].iloc[0] == 0.0
    assert visualizer.df["overtime"].iloc[1] == 0.0  # -1.5 < 0, so should be 0.0 (negative overtime handling)
    assert visualizer.df["overtime"].iloc[2] == 2.0


@pytest.mark.fast
def test_make_logbook_robust_empty_dataframe() -> None:
    """Test make_logbook_robust with empty DataFrame."""
    df = pd.DataFrame(columns=["date", "work_time", "overtime"])

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    # Should handle empty DataFrame gracefully
    assert visualizer.df.empty
    assert "date" in visualizer.df.columns
    assert "work_time" in visualizer.df.columns
    assert "overtime" in visualizer.df.columns


@pytest.mark.fast
def test_make_logbook_robust_zero_overtime_preserved() -> None:
    """Test that zero overtime values are preserved."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "work_time": ["8.0", "8.0"],
            "overtime": ["0.0", "0"],
        },
    )

    data = {
        "full_format": "%d.%m.%Y %H:%M:%S",
        "color_scheme": "ocean",
        "num_months": 12,
        "standard_work_hours": 8.0,
        "work_days": [0, 1, 2, 3, 4],
    }

    visualizer = viz.Visualizer(df, data)

    # Zero values should be preserved
    assert visualizer.df["overtime"].iloc[0] == 0.0
    assert visualizer.df["overtime"].iloc[1] == 0.0

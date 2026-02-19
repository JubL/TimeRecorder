"""Unit tests for edge cases in the Visualizer make_logbook_robust method."""

import pandas as pd
import pytest

import src.config_utils as cu
import src.visualizer as viz


@pytest.mark.fast
def test_make_logbook_robust_invalid_time_handling(sample_config: dict) -> None:
    """Test make_logbook_robust with invalid time strings."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "invalid_time", "25:00:00"],  # Invalid times
            "work_time": [8.0, 7.5, 8.5],
            "overtime": [0.0, 0.5, 0.5],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # Invalid times should result in work_time being set to -standard_work_hours
    assert visualizer.df["work_time"].iloc[1] == -8.0  # invalid_time
    assert visualizer.df["work_time"].iloc[2] == -8.0  # 25:00:00


@pytest.mark.fast
def test_make_logbook_robust_mixed_valid_invalid_times(sample_config: dict) -> None:
    """Test make_logbook_robust with mix of valid and invalid times."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024"],
            "start_time": ["08:00:00", "invalid", "14:30:15", ""],  # Mixed validity
            "work_time": [8.0, 7.5, 8.5, 7.0],
            "overtime": [0.0, 0.5, 0.5, 0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # Valid times should keep original work_time
    assert visualizer.df["work_time"].iloc[0] == 8.0  # Valid time
    assert visualizer.df["work_time"].iloc[2] == 8.5  # Valid time

    # Invalid times should be set to -standard_work_hours
    assert visualizer.df["work_time"].iloc[1] == -8.0  # invalid
    assert visualizer.df["work_time"].iloc[3] == -8.0  # empty string


@pytest.mark.fast
def test_make_logbook_robust_none_start_time(sample_config: dict) -> None:
    """Test make_logbook_robust with None start_time values."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": [None, "08:00:00"],
            "work_time": [8.0, 7.5],
            "overtime": [0.0, 0.5],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # None start_time should result in work_time being set to -standard_work_hours
    assert visualizer.df["work_time"].iloc[0] == -8.0  # None start_time
    assert visualizer.df["work_time"].iloc[1] == 7.5  # Valid start_time


@pytest.mark.fast
def test_make_logbook_robust_nan_start_time(sample_config: dict) -> None:
    """Test make_logbook_robust with NaN/NA start_time values (treated as invalid)."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": [pd.NA, "08:00:00"],
            "work_time": [8.0, 7.5],
            "overtime": [0.0, 0.5],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # NA/NaN start_time should be treated as invalid -> work_time set to -standard_work_hours
    assert visualizer.df["work_time"].iloc[0] == -8.0  # pd.NA start_time
    assert visualizer.df["work_time"].iloc[1] == 7.5  # valid start_time


@pytest.mark.fast
def test_make_logbook_robust_extreme_numeric_values(sample_config: dict) -> None:
    """Test make_logbook_robust with extreme numeric values."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00"],
            "work_time": [1e10, -1e10, 0.0],  # Very large, very negative, zero
            "overtime": [1e-10, -1e-10, 0.0],  # Very small, very negative, zero
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # All values should be converted to numeric and handled appropriately
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # Negative overtime should be set to 0.0
    assert visualizer.df["overtime"].iloc[1] == 0.0  # -1e-10 should become 0.0


@pytest.mark.fast
def test_make_logbook_robust_string_numeric_conversion(sample_config: dict) -> None:
    """Test make_logbook_robust with various string numeric formats."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00", "08:00:00"],
            "work_time": ["8", "8.5", "8,5", "8.5e0"],  # Different string formats
            "overtime": ["0", "0.5", "0,5", "0.5e0"],  # Different string formats
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # All should be converted to numeric
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # Check specific conversions
    assert visualizer.df["work_time"].iloc[0] == 8.0  # "8"
    assert visualizer.df["work_time"].iloc[1] == 8.5  # "8.5"
    assert visualizer.df["work_time"].iloc[2] == 0.0  # "8,5" - invalid, becomes 0.0
    assert visualizer.df["work_time"].iloc[3] == 8.5  # "8.5e0"


@pytest.mark.fast
def test_make_logbook_robust_boolean_values(sample_config: dict) -> None:
    """Test make_logbook_robust with boolean values in numeric columns."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [True, False],  # Boolean values
            "overtime": [False, True],  # Boolean values
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # Boolean values are converted to numeric by pd.to_numeric
    # They become bool dtype which is considered numeric
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # Boolean values remain as boolean
    assert visualizer.df["work_time"].iloc[0]  # is True
    assert not visualizer.df["work_time"].iloc[1]  # is False
    assert not visualizer.df["overtime"].iloc[0]  # is False
    assert visualizer.df["overtime"].iloc[1]  # is True


@pytest.mark.fast
def test_make_logbook_robust_complex_invalid_strings(sample_config: dict) -> None:
    """Test make_logbook_robust with complex invalid string values."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00", "08:00:00"],
            "work_time": ["8.5.5", "8-5", "8+5", "8*5"],  # Complex invalid strings
            "overtime": ["0.5.5", "0-5", "0+5", "0*5"],  # Complex invalid strings
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # All invalid strings should be converted to NaN and then filled with 0.0
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # All should be 0.0 due to invalid conversion
    assert visualizer.df["work_time"].iloc[0] == 0.0
    assert visualizer.df["work_time"].iloc[1] == 0.0
    assert visualizer.df["work_time"].iloc[2] == 0.0
    assert visualizer.df["work_time"].iloc[3] == 0.0
    assert visualizer.df["overtime"].iloc[0] == 0.0
    assert visualizer.df["overtime"].iloc[1] == 0.0
    assert visualizer.df["overtime"].iloc[2] == 0.0
    assert visualizer.df["overtime"].iloc[3] == 0.0


@pytest.mark.fast
def test_make_logbook_robust_unicode_values(sample_config: dict) -> None:
    """Test make_logbook_robust with unicode numeric values."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": ["8", "8.5"],  # Unicode numbers
            "overtime": ["0", "0.5"],  # Unicode numbers
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # Unicode numbers are actually converted to numeric by pd.to_numeric
    assert pd.api.types.is_numeric_dtype(visualizer.df["work_time"])
    assert pd.api.types.is_numeric_dtype(visualizer.df["overtime"])

    # Unicode numbers are converted to regular numbers
    assert visualizer.df["work_time"].iloc[0] == 8.0
    assert visualizer.df["work_time"].iloc[1] == 8.5
    assert visualizer.df["overtime"].iloc[0] == 0.0
    assert visualizer.df["overtime"].iloc[1] == 0.5

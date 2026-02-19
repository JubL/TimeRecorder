"""Unit tests for the Visualizer get_rolling_average method."""

import pandas as pd
import pytest

import src.config_utils as cu
import src.visualizer as viz


# Expected cases
@pytest.mark.fast
def test_get_rolling_average_normal_operation(sample_config: dict) -> None:
    """Test get_rolling_average with normal operation and multiple data points."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "05.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00", "08:00:00", "08:00:00"],
            "work_time": [8.0, 7.5, 9.0, 8.5, 7.0],
            "overtime": [0.0, 0.5, 1.0, 0.5, 0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average(window=3)

    # Should return a Series with rolling averages
    assert isinstance(result, pd.Series)
    assert len(result) == 5  # All 5 rows have work_time > 0
    # First value should be the first work_time (window=3, min_periods=1)
    assert result.iloc[0] == 8.0
    # Third value should be average of first 3 values
    assert result.iloc[2] == pytest.approx((8.0 + 7.5 + 9.0) / 3, rel=1e-6)


@pytest.mark.fast
def test_get_rolling_average_different_window_sizes(sample_config: dict) -> None:
    """Test get_rolling_average with different window sizes."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "05.01.2024"],
            "start_time": ["08:00:00"] * 5,
            "work_time": [8.0, 7.0, 9.0, 8.0, 7.0],
            "overtime": [0.0] * 5,
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)

    # Window size 1
    result_1 = visualizer.get_rolling_average(window=1)
    assert len(result_1) == 5
    assert result_1.iloc[0] == 8.0
    assert result_1.iloc[1] == 7.0

    # Window size 2
    result_2 = visualizer.get_rolling_average(window=2)
    assert len(result_2) == 5
    assert result_2.iloc[1] == pytest.approx((8.0 + 7.0) / 2, rel=1e-6)

    # Window size larger than data points (should still work with min_periods=1)
    result_10 = visualizer.get_rolling_average(window=10)
    assert len(result_10) == 5
    assert result_10.iloc[0] == 8.0


@pytest.mark.fast
def test_get_rolling_average_single_data_point(sample_config: dict) -> None:
    """Test get_rolling_average with a single data point."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average(window=5)

    assert isinstance(result, pd.Series)
    assert len(result) == 1
    assert result.iloc[0] == 8.0


@pytest.mark.fast
def test_get_rolling_average_filters_positive_work_time(sample_config: dict) -> None:
    """Test that get_rolling_average only includes rows with work_time > 0."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024"],
            "start_time": ["08:00:00"] * 4,
            "work_time": [8.0, 0.0, -8.0, 7.5],  # Mix of positive, zero, and negative
            "overtime": [0.0] * 4,
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average(window=2)

    # Should only include rows with work_time > 0 (first and last)
    assert isinstance(result, pd.Series)
    assert len(result) == 2  # Only 2 rows have work_time > 0
    assert result.iloc[0] == 8.0
    assert result.iloc[1] == pytest.approx((8.0 + 7.5) / 2, rel=1e-6)


# Edge cases
@pytest.mark.fast
def test_get_rolling_average_zero_window(sample_config: dict) -> None:
    """Test get_rolling_average returns 0.0 when window is 0 (lines 185-186)."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00"],
            "work_time": [8.0, 7.5, 9.0],
            "overtime": [0.0, 0.5, 1.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average(window=0)

    assert isinstance(result, pd.Series)
    assert result.empty


@pytest.mark.fast
def test_get_rolling_average_none_window(sample_config: dict) -> None:
    """Test get_rolling_average returns 0.0 when window is None (falsy)."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [8.0, 7.5],
            "overtime": [0.0, 0.5],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average(window=None)  # type: ignore [arg-type]

    assert isinstance(result, pd.Series)
    assert result.empty


@pytest.mark.fast
def test_get_rolling_average_false_window(sample_config: dict) -> None:
    """Test get_rolling_average returns 0.0 when window is False (falsy)."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [8.0, 7.5],
            "overtime": [0.0, 0.5],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average(window=False)

    assert isinstance(result, pd.Series)
    assert result.empty


@pytest.mark.fast
def test_get_rolling_average_empty_dataframe(sample_config: dict) -> None:
    """Test get_rolling_average with empty DataFrame."""
    df = pd.DataFrame(
        {
            "date": [],
            "start_time": [],
            "work_time": [],
            "overtime": [],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average(window=5)

    assert isinstance(result, pd.Series)
    assert len(result) == 0


@pytest.mark.fast
def test_get_rolling_average_all_zero_work_time(sample_config: dict) -> None:
    """Test get_rolling_average when all work_time values are 0 or negative."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00"] * 3,
            "work_time": [0.0, -8.0, 0.0],  # All zero or negative
            "overtime": [0.0] * 3,
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average(window=3)

    # Should return empty Series since no rows have work_time > 0
    assert isinstance(result, pd.Series)
    assert len(result) == 0


@pytest.mark.fast
def test_get_rolling_average_default_window(sample_config: dict) -> None:
    """Test get_rolling_average with default window parameter."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "05.01.2024"],
            "start_time": ["08:00:00"] * 5,
            "work_time": [8.0, 7.5, 9.0, 8.5, 7.0],
            "overtime": [0.0] * 5,
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12
    visualizer = viz.Visualizer(df, visualization_config)
    result = visualizer.get_rolling_average()  # Uses default window=10

    assert isinstance(result, pd.Series)
    assert len(result) == 5
    assert result.iloc[0] == 8.0

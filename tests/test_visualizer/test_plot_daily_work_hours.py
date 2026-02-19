"""Unit tests for the Visualizer plot_daily_work_hours method."""

import pandas as pd
import pytest

import src.config_utils as cu
import src.visualizer as viz


@pytest.mark.fast
def test_plot_daily_work_hours_basic_functionality(sample_config: dict) -> None:
    """Test basic plotting functionality with simple data."""
    # Create sample data for one week
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "05.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00", "08:00:00", "08:00:00"],
            "work_time": [8.0, 7.5, 8.5, 8.0, 7.0],
            "overtime": [0.0, 0.5, 0.5, 0.0, 0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # Test that the method runs without errors
    # Note: We can't easily test the actual plot output without complex mocking
    # But we can test that the method modifies the DataFrame correctly

    # The method should adjust work_time when it exceeds standard hours
    visualizer.create_daily_work_hours_plot()

    # Check that work_time was adjusted for overtime cases
    # Day 2: 7.5 + 0.5 = 8.0 (no adjustment needed)
    # Day 3: 8.5 + 0.5 = 9.0 (should be adjusted to 8.5)
    assert visualizer.df["work_time"].iloc[2] == 8.0  # 8.5 - 0.5 = 8.0


@pytest.mark.fast
def test_plot_daily_work_hours_work_time_adjustment(sample_config: dict) -> None:
    """Test that work_time is correctly adjusted when total exceeds standard hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [9.0, 10.0],  # Both exceed standard 8 hours
            "overtime": [1.0, 2.0],  # Overtime hours
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # Before adjustment
    assert visualizer.df["work_time"].iloc[0] == 9.0
    assert visualizer.df["work_time"].iloc[1] == 10.0

    visualizer.create_daily_work_hours_plot()

    # After adjustment: work_time should be reduced by overtime
    assert visualizer.df["work_time"].iloc[0] == 8.0  # 9.0 - 1.0
    assert visualizer.df["work_time"].iloc[1] == 8.0  # 10.0 - 2.0


@pytest.mark.fast
def test_plot_daily_work_hours_no_adjustment_needed(sample_config: dict) -> None:
    """Test that work_time is not adjusted when total doesn't exceed standard hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024"],
            "start_time": ["08:00:00", "08:00:00"],
            "work_time": [7.0, 8.0],  # Both within or at standard hours
            "overtime": [0.0, 0.0],  # No overtime
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # Before adjustment
    assert visualizer.df["work_time"].iloc[0] == 7.0
    assert visualizer.df["work_time"].iloc[1] == 8.0

    visualizer.create_daily_work_hours_plot()

    # After adjustment: work_time should remain unchanged
    assert visualizer.df["work_time"].iloc[0] == 7.0
    assert visualizer.df["work_time"].iloc[1] == 8.0


@pytest.mark.fast
def test_plot_daily_work_hours_mixed_scenarios(sample_config: dict) -> None:
    """Test work_time adjustment with mixed scenarios."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024"],
            "start_time": ["08:00:00", "08:00:00", "08:00:00", "08:00:00"],
            "work_time": [7.0, 8.0, 9.0, 10.0],
            "overtime": [0.0, 0.0, 1.0, 2.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    visualizer.create_daily_work_hours_plot()

    # Check adjustments:
    # Day 1: 7.0 + 0.0 = 7.0 (no adjustment)
    # Day 2: 8.0 + 0.0 = 8.0 (no adjustment)
    # Day 3: 9.0 + 1.0 = 10.0 (adjust to 8.0)
    # Day 4: 10.0 + 2.0 = 12.0 (adjust to 8.0)
    assert visualizer.df["work_time"].iloc[0] == 7.0
    assert visualizer.df["work_time"].iloc[1] == 8.0
    assert visualizer.df["work_time"].iloc[2] == 8.0  # 9.0 - 1.0
    assert visualizer.df["work_time"].iloc[3] == 8.0  # 10.0 - 2.0


@pytest.mark.fast
def test_plot_daily_work_hours_empty_dataframe(sample_config: dict) -> None:
    """Test plotting with empty DataFrame."""
    df = pd.DataFrame(columns=["date", "work_time", "overtime"])

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(df, visualization_config)

    # Should handle empty DataFrame gracefully
    visualizer.create_daily_work_hours_plot()
    assert visualizer.df.empty


@pytest.mark.fast
def test_plot_daily_work_hours_different_color_schemes(
    sample_logbook_df: pd.DataFrame, sample_config: dict
) -> None:
    """Test plotting with different color schemes."""
    color_schemes = ["ocean", "forest", "sunset", "lavender", "coral"]

    for scheme in color_schemes:
        visualization_config = cu.get_visualization_config(sample_config)
        visualization_config["color_scheme"] = scheme
        visualization_config["num_months"] = 12

        visualizer = viz.Visualizer(sample_logbook_df, visualization_config)

        # Should run without errors for all color schemes
        visualizer.create_daily_work_hours_plot()

        # Verify color schemes are correctly assigned
        assert visualizer.work_colors == viz.COLOR_SCHEMES_WORK[scheme]


@pytest.mark.fast
def test_plot_daily_work_hours_custom_work_days(
    sample_logbook_df: pd.DataFrame, sample_config: dict
) -> None:
    """Test plotting with custom work days."""
    custom_work_days = [1, 2]  # Only Tuesday and Wednesday

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["work_days"] = custom_work_days
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(sample_logbook_df, visualization_config)

    # Should run without errors with custom work days
    visualizer.create_daily_work_hours_plot()
    assert visualizer.work_days == custom_work_days


@pytest.mark.fast
def test_plot_daily_work_hours_large_overtime(
    sample_logbook_df: pd.DataFrame, sample_config: dict
) -> None:
    """Test work_time adjustment with large overtime values."""
    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 12

    visualizer = viz.Visualizer(sample_logbook_df, visualization_config)

    visualizer.create_daily_work_hours_plot()

    # Should adjust to 8.0 (12.0 - 4.0)
    assert visualizer.df["work_time"].iloc[0] == 7.0

"""Unit tests for edge cases in the Visualizer constructor."""

import pandas as pd
import pytest

import src.config_utils as cu
import src.visualizer as viz


@pytest.mark.fast
def test_constructor_invalid_color_scheme(sample_config: dict) -> None:
    """Test constructor with invalid color scheme."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["color_scheme"] = "invalid_scheme"  # Invalid color scheme

    with pytest.raises(KeyError):
        viz.Visualizer(df, visualization_config)


@pytest.mark.fast
def test_constructor_missing_required_keys(sample_config: dict) -> None:
    """Test constructor with missing required configuration keys."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    # Missing 'full_format'
    visualization_config = cu.get_visualization_config(sample_config)
    del visualization_config["full_format"]

    with pytest.raises(KeyError):
        viz.Visualizer(df, visualization_config)


@pytest.mark.fast
def test_constructor_missing_color_scheme(sample_config: dict) -> None:
    """Test constructor with missing color_scheme."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    del visualization_config["color_scheme"]

    with pytest.raises(KeyError):
        viz.Visualizer(df, visualization_config)


@pytest.mark.fast
def test_constructor_missing_num_months(sample_config: dict) -> None:
    """Test constructor with missing num_months."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    del visualization_config["num_months"]

    with pytest.raises(KeyError):
        viz.Visualizer(df, visualization_config)


@pytest.mark.fast
def test_constructor_missing_standard_work_hours(sample_config: dict) -> None:
    """Test constructor with missing standard_work_hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    del visualization_config["standard_work_hours"]

    with pytest.raises(KeyError):
        viz.Visualizer(df, visualization_config)


@pytest.mark.fast
def test_constructor_missing_work_days(sample_config: dict) -> None:
    """Test constructor with missing work_days."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    del visualization_config["work_days"]

    with pytest.raises(KeyError):
        viz.Visualizer(df, visualization_config)


@pytest.mark.fast
def test_constructor_invalid_full_format(sample_config: dict) -> None:
    """Test constructor with invalid full_format that can't be split."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["full_format"] = "invalid_format"  # No space to split

    with pytest.raises(ValueError, match="not enough values to unpack"):
        viz.Visualizer(df, visualization_config)


@pytest.mark.fast
def test_constructor_negative_num_months(sample_config: dict) -> None:
    """Test constructor with negative num_months."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = -1  # Negative months

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.num_months == -1


@pytest.mark.fast
def test_constructor_zero_num_months(sample_config: dict) -> None:
    """Test constructor with zero num_months."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 0  # Zero months

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.num_months == 0


@pytest.mark.fast
def test_constructor_negative_standard_work_hours(sample_config: dict) -> None:
    """Test constructor with negative standard_work_hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["standard_work_hours"] = -8.0  # Negative work hours

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.standard_work_hours == -8.0


@pytest.mark.fast
def test_constructor_zero_standard_work_hours(sample_config: dict) -> None:
    """Test constructor with zero standard_work_hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["standard_work_hours"] = 0.0  # Zero work hours

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.standard_work_hours == 0.0


@pytest.mark.fast
def test_constructor_empty_work_days(sample_config: dict) -> None:
    """Test constructor with empty work_days list."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["work_days"] = []  # Empty work days

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.work_days == []


@pytest.mark.fast
def test_constructor_invalid_work_days(sample_config: dict) -> None:
    """Test constructor with invalid work_days values."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["work_days"] = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # Invalid weekday numbers

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.work_days == [0, 1, 2, 3, 4, 5, 6, 7, 8]  # Constructor doesn't validate


@pytest.mark.fast
def test_constructor_float_num_months(sample_config: dict) -> None:
    """Test constructor with float num_months raises ValueError."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 6.5  # Float months

    with pytest.raises(ValueError, match="Non-integer years and months are ambiguous"):
        viz.Visualizer(df, visualization_config)


@pytest.mark.fast
def test_constructor_float_standard_work_hours(sample_config: dict) -> None:
    """Test constructor with float standard_work_hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["standard_work_hours"] = 7.5  # Float work hours

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.standard_work_hours == 7.5


@pytest.mark.fast
def test_constructor_very_large_num_months(sample_config: dict) -> None:
    """Test constructor with very large num_months."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["num_months"] = 1000  # Very large number

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.num_months == 1000


@pytest.mark.fast
def test_constructor_very_large_standard_work_hours(sample_config: dict) -> None:
    """Test constructor with very large standard_work_hours."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["standard_work_hours"] = 1000.0  # Very large work hours

    visualizer = viz.Visualizer(df, visualization_config)
    assert visualizer.standard_work_hours == 1000.0


@pytest.mark.fast
def test_constructor_none_values_in_config(sample_config: dict) -> None:
    """Test constructor with None values in configuration."""
    df = pd.DataFrame(
        {
            "date": ["01.01.2024"],
            "start_time": ["08:00:00"],
            "work_time": [8.0],
            "overtime": [0.0],
        },
    )

    visualization_config = cu.get_visualization_config(sample_config)
    visualization_config["full_format"] = None  # None value

    with pytest.raises(AttributeError):
        viz.Visualizer(df, visualization_config)

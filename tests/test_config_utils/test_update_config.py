"""Tests for the update_config function in config_utils module."""

import argparse

import pytest

import src.config_utils as cu


@pytest.mark.fast
def test_update_config_no_args() -> None:
    """Test update_config when no arguments are provided."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:00",
        },
        "data_processing": {
            "use_boot_time": True,
            "logging_enabled": False,
        },
    }

    args = argparse.Namespace()

    result = cu.update_config(config, args)

    # Should return a copy of the original config unchanged
    assert result == config
    # Should return a shallow copy (different object reference)
    assert result is not config


@pytest.mark.fast
def test_update_config_single_arg() -> None:
    """Test update_config with a single argument."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
        },
        "data_processing": {
            "use_boot_time": True,
        },
    }

    args = argparse.Namespace(date="26.07.2025")

    result = cu.update_config(config, args)

    # Check that the date was updated
    assert result["time_tracking"]["date"] == "26.07.2025"
    # Check that other values remain unchanged
    assert result["time_tracking"]["start_time"] == "07:00"
    assert result["data_processing"]["use_boot_time"] is True
    # Note: The function uses shallow copy, so nested dicts are shared
    # The original config will be modified for nested dictionaries
    assert config["time_tracking"]["date"] == "26.07.2025"


@pytest.mark.fast
def test_update_config_multiple_args() -> None:
    """Test update_config with multiple arguments."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:00",
            "lunch_break_duration": 60,
        },
        "data_processing": {
            "use_boot_time": True,
            "logging_enabled": False,
            "auto_squash": True,
        },
        "display": {
            "show_tail": 5,
            "calculate_weekly_hours": True,
        },
    }

    args = argparse.Namespace(
        date="26.07.2025",
        start="08:00",
        lunch=45,
        boot=False,
        tail=10,
    )

    result = cu.update_config(config, args)

    # Check that all specified values were updated
    assert result["time_tracking"]["date"] == "26.07.2025"
    assert result["time_tracking"]["start_time"] == "08:00"
    assert result["time_tracking"]["lunch_break_duration"] == 45
    assert result["data_processing"]["use_boot_time"] is False
    assert result["display"]["show_tail"] == 10
    # Check that unspecified values remain unchanged
    assert result["time_tracking"]["end_time"] == "17:00"
    assert result["data_processing"]["logging_enabled"] is False
    assert result["display"]["calculate_weekly_hours"] is True


@pytest.mark.fast
def test_update_config_creates_missing_sections() -> None:
    """Test that update_config creates missing sections when needed."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
        },
    }

    args = argparse.Namespace(
        boot=True,
        log=True,
        plot=False,
        color_scheme="ocean",
    )

    result = cu.update_config(config, args)

    # Check that missing sections were created
    assert "data_processing" in result
    assert "visualization" in result
    # Check that values were set correctly
    assert result["data_processing"]["use_boot_time"] is True
    assert result["data_processing"]["logging_enabled"] is True
    assert result["visualization"]["plot"] is False
    assert result["visualization"]["color_scheme"] == "ocean"
    # Check that original section remains unchanged
    assert result["time_tracking"]["date"] == "25.07.2025"


@pytest.mark.fast
def test_update_config_different_data_types() -> None:
    """Test update_config with different data types."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
        },
        "data_processing": {
            "use_boot_time": True,
        },
    }

    args = argparse.Namespace(
        date="26.07.2025",  # String
        lunch=30,  # Integer
        boot=False,  # Boolean
        tail=5,  # Integer
        num_months=12,  # Integer
        plot=True,  # Boolean
    )

    result = cu.update_config(config, args)

    # Check that different data types are handled correctly
    assert isinstance(result["time_tracking"]["date"], str)
    assert isinstance(result["time_tracking"]["lunch_break_duration"], int)
    assert isinstance(result["data_processing"]["use_boot_time"], bool)
    assert isinstance(result["display"]["show_tail"], int)
    assert isinstance(result["visualization"]["num_months"], int)
    assert isinstance(result["visualization"]["plot"], bool)


@pytest.mark.fast
def test_update_config_none_values_ignored() -> None:
    """Test that None values in args are ignored."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
        },
        "data_processing": {
            "use_boot_time": True,
        },
    }

    args = argparse.Namespace(
        date="26.07.2025",
        start=None,  # This should be ignored
        boot=None,  # This should be ignored
    )

    result = cu.update_config(config, args)

    # Check that only non-None values were updated
    assert result["time_tracking"]["date"] == "26.07.2025"
    assert result["time_tracking"]["start_time"] == "07:00"  # Unchanged
    assert result["data_processing"]["use_boot_time"] is True  # Unchanged


@pytest.mark.fast
def test_update_config_missing_attributes_ignored() -> None:
    """Test that missing attributes in args are ignored."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
        },
        "data_processing": {
            "use_boot_time": True,
        },
    }

    args = argparse.Namespace(
        date="26.07.2025",
        # start and boot attributes don't exist
    )

    result = cu.update_config(config, args)

    # Check that only existing attributes were processed
    assert result["time_tracking"]["date"] == "26.07.2025"
    assert result["data_processing"]["use_boot_time"] is True  # Unchanged


@pytest.mark.fast
def test_update_config_all_argument_mappings() -> None:
    """Test all argument mappings defined in the function."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
            "start_time": "07:00",
            "end_time": "17:00",
            "lunch_break_duration": 60,
        },
        "data_processing": {
            "use_boot_time": True,
            "logging_enabled": False,
            "auto_squash": True,
            "add_missing_days": True,
        },
        "logging": {
            "log_path": "default.csv",
        },
        "display": {
            "calculate_weekly_hours": True,
            "calculate_daily_overhours": True,
            "show_tail": 5,
        },
        "visualization": {
            "plot": True,
            "num_months": 12,
            "color_scheme": "default",
        },
    }

    args = argparse.Namespace(
        # Data processing settings
        boot=False,
        log=True,
        no_squash=False,
        no_missing=False,
        # Time tracking settings
        date="26.07.2025",
        start="08:00",
        end="18:00",
        end_now=True,
        lunch=45,
        # Logging settings
        logbook="custom.csv",
        # Display settings
        no_weekly=False,
        no_overhours=False,
        tail=10,
        # Visualization settings
        plot=False,
        num_months=6,
        color_scheme="ocean",
    )

    result = cu.update_config(config, args)

    # Check all data processing settings
    assert result["data_processing"]["use_boot_time"] is False
    assert result["data_processing"]["logging_enabled"] is True
    assert result["data_processing"]["auto_squash"] is False
    assert result["data_processing"]["add_missing_days"] is False

    # Check all time tracking settings
    assert result["time_tracking"]["date"] == "26.07.2025"
    assert result["time_tracking"]["start_time"] == "08:00"
    assert result["time_tracking"]["end_time"] == "18:00"
    assert result["time_tracking"]["end_now"] is True
    assert result["time_tracking"]["lunch_break_duration"] == 45

    # Check logging settings
    assert result["logging"]["log_path"] == "custom.csv"

    # Check display settings
    assert result["display"]["calculate_weekly_hours"] is False
    assert result["display"]["calculate_daily_overhours"] is False
    assert result["display"]["show_tail"] == 10

    # Check visualization settings
    assert result["visualization"]["plot"] is False
    assert result["visualization"]["num_months"] == 6
    assert result["visualization"]["color_scheme"] == "ocean"


@pytest.mark.fast
def test_update_config_deep_nesting() -> None:
    """Test that deeply nested paths are created correctly."""
    config = {
        "existing_section": {
            "existing_key": "existing_value",
        },
    }

    args = argparse.Namespace(
        boot=True,  # Should create data_processing.use_boot_time
        plot=False,  # Should create visualization.plot
    )

    result = cu.update_config(config, args)

    # Check that deeply nested paths were created
    assert "data_processing" in result
    assert "visualization" in result
    assert result["data_processing"]["use_boot_time"] is True
    assert result["visualization"]["plot"] is False
    # Check that existing sections remain unchanged
    assert result["existing_section"]["existing_key"] == "existing_value"


@pytest.mark.fast
def test_update_config_empty_config() -> None:
    """Test update_config with an empty configuration."""
    config = {}

    args = argparse.Namespace(
        date="26.07.2025",
        boot=True,
        plot=False,
    )

    result = cu.update_config(config, args)

    # Check that sections were created and values set
    assert "time_tracking" in result
    assert "data_processing" in result
    assert "visualization" in result
    assert result["time_tracking"]["date"] == "26.07.2025"
    assert result["data_processing"]["use_boot_time"] is True
    assert result["visualization"]["plot"] is False


@pytest.mark.fast
def test_update_config_return_type() -> None:
    """Test that update_config returns a dictionary."""
    config = {
        "time_tracking": {
            "date": "25.07.2025",
        },
    }

    args = argparse.Namespace(date="26.07.2025")

    result = cu.update_config(config, args)

    assert isinstance(result, dict)

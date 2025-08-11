"""
Configuration utilities for the TimeRecorder project.

This module provides functionality to load and parse YAML configuration files,
with support for default values and configuration validation.
"""

import argparse
import pathlib

import yaml

import src.logging_utils as lu

# Set up logger
logger = lu.setup_logger(__name__)


def load_config(config_path: pathlib.Path) -> dict:
    """
    Load configuration from a YAML file.

    Parameters
    ----------
    config_path : pathlib.Path
        Path to the YAML configuration file.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the configuration parameters.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    yaml.YAMLError
        If the YAML file is malformed.
    """
    if not config_path.exists():
        msg = f"Configuration file not found: {config_path}"
        raise FileNotFoundError(msg)

    try:
        with config_path.open(encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError:
        msg = f"Error parsing YAML file {config_path}"
        logger.exception(msg)
        raise
    except Exception:
        msg = f"Error loading configuration file {config_path}"
        logger.exception(msg)
        raise
    else:
        msg = f"Configuration loaded from {config_path}"
        logger.debug(msg)
        return config


def get_time_recorder_config(config: dict) -> dict:
    """
    Extract TimeRecorder-specific configuration from the main config.

    Parameters
    ----------
    config : Dict[str, Any]
        The main configuration dictionary.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing TimeRecorder parameters.
    """
    time_tracking = config.get("time_tracking", {})
    work_schedule = config.get("work_schedule", {})

    return {
        "date": time_tracking.get("date", "01.08.2025"),
        "start_time": time_tracking.get("start_time", "07:00"),
        "end_time": time_tracking.get("end_time", "17:25"),
        "end_now": time_tracking.get("end_now", False),
        "lunch_break_duration": time_tracking.get("lunch_break_duration", 60),
        "full_format": time_tracking.get("full_format", "%d.%m.%Y %H:%M:%S"),
        "timezone": work_schedule.get("timezone", "Europe/Berlin"),
    }


def get_logbook_config(config: dict) -> dict:
    """
    Extract Logbook-specific configuration from the main config.

    Parameters
    ----------
    config : Dict[str, Any]
        The main configuration dictionary.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing Logbook parameters.
    """
    logging_config = config.get("logging", {})
    time_tracking = config.get("time_tracking", {})
    holidays = config.get("holidays", {})
    work_schedule = config.get("work_schedule", {})

    return {
        "log_path": pathlib.Path.cwd() / logging_config.get("log_path", "timereport_logbook.txt"),
        "full_format": time_tracking.get("full_format", "%d.%m.%Y %H:%M:%S"),
        "holidays": holidays.get("country", "DE"),
        "subdivision": holidays.get("subdivision", "HE"),
        "standard_work_hours": work_schedule.get("standard_work_hours", 8),
        "work_days": work_schedule.get("work_days", [0, 1, 2, 3, 4]),
    }


def get_display_config(config: dict) -> dict:
    """
    Extract display configuration from the main config.

    Parameters
    ----------
    config : Dict[str, Any]
        The main configuration dictionary.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing display parameters.
    """
    display_config = config.get("display", {})

    return {
        "show_tail": display_config.get("show_tail", 4),
        "calculate_weekly_hours": display_config.get("calculate_weekly_hours", True),
        "calculate_daily_overhours": display_config.get("calculate_daily_overhours", True),
    }


def get_processing_config(config: dict) -> dict:
    """
    Extract data processing configuration from the main config.

    Parameters
    ----------
    config : Dict[str, Any]
        The main configuration dictionary.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing processing parameters.
    """
    data_processing = config.get("data_processing", {})
    display = config.get("display", {})

    return {
        "use_boot_time": data_processing.get("use_boot_time", True),
        "log_enabled": data_processing.get("logging_enabled", False),
        "auto_squash": data_processing.get("auto_squash", True),
        "add_missing_days": data_processing.get("add_missing_days", True),
        "calculate_weekly_hours": display.get("calculate_weekly_hours", True),
        "calculate_daily_overhours": display.get("calculate_daily_overhours", True),
    }


def validate_config(config: dict) -> bool:
    """
    Validate the configuration dictionary.

    Parameters
    ----------
    config : Dict[str, Any]
        The configuration dictionary to validate.

    Returns
    -------
    bool
        True if configuration is valid, False otherwise.
    """
    required_sections = ["time_tracking", "logging", "work_schedule"]

    for section in required_sections:
        if section not in config:
            msg = f"Missing required configuration section: {section}"
            logger.error(msg)
            return False

    # Validate time tracking settings
    time_tracking = config.get("time_tracking", {})
    required_time_fields = ["date", "start_time", "end_time", "lunch_break_duration"]

    for field in required_time_fields:
        if field not in time_tracking:
            msg = f"Missing required time tracking field: {field}"
            logger.error(msg)
            return False

    # Validate logging settings
    logging_config = config.get("logging", {})
    if "log_path" not in logging_config:
        logger.error("Missing required logging field: log_path")
        return False

    logger.debug("Configuration validation passed")
    return True


def create_default_config(config_path: pathlib.Path) -> None:
    """
    Create a default configuration file if it doesn't exist.

    Parameters
    ----------
    config_path : pathlib.Path
        Path where the default configuration file should be created.

    Raises
    ------
    yaml.YAMLError
        If the YAML file is malformed.
    """
    if config_path.exists():
        msg = f"Configuration file already exists: {config_path}"
        logger.debug(msg)
        return

    default_config: dict = {
        "time_tracking": {
            "date": "01.08.2025",
            "start_time": "07:30",
            "end_time": "17:25",
            "lunch_break_duration": 60,
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
        "logging": {
            "log_path": "timereport_logbook.txt",
            "log_level": "INFO",
        },
        "work_schedule": {
            "standard_work_hours": 8,
            "work_days": [0, 1, 2, 3, 4],
            "timezone": "Europe/Berlin",
        },
        "holidays": {
            "country": "DE",
            "subdivision": "HE",
        },
        "data_processing": {
            "use_boot_time": True,
            "logging_enabled": False,
            "auto_squash": True,
            "add_missing_days": True,
        },
        "display": {
            "calculate_weekly_hours": True,
            "calculate_daily_overhours": True,
            "show_tail": 4,
        },
    }

    try:
        with config_path.open("w", encoding="utf-8") as file:
            yaml.dump(default_config, file, default_flow_style=False, sort_keys=False)
        msg = f"Default configuration file created: {config_path}"
        logger.debug(msg)
    except yaml.YAMLError:
        logger.exception("Error creating default configuration file")
        raise


def update_config(config: dict, args: argparse.Namespace) -> dict:
    """
    Update the configuration dictionary with the values from the command line arguments.

    Parameters
    ----------
    config : dict
        The original configuration dictionary.
    args : argparse.Namespace
        Parsed command line arguments.

    Returns
    -------
    dict
        Updated configuration dictionary with command line argument values merged in.
    """
    # Create a copy of the config to avoid modifying the original
    updated_config = config.copy()

    # Define argument mappings: (arg_name, config_path, transform_function)
    # transform_function can be None for direct assignment, or a function for custom logic
    arg_mappings = [
        # Data processing settings
        ("boot", "data_processing.use_boot_time"),
        ("log", "data_processing.logging_enabled"),
        ("no_squash", "data_processing.auto_squash"),
        ("no_missing", "data_processing.add_missing_days"),
        # Time tracking settings
        ("date", "time_tracking.date"),
        ("start", "time_tracking.start_time"),
        ("end", "time_tracking.end_time"),
        ("end_now", "time_tracking.end_now"),
        ("lunch", "time_tracking.lunch_break_duration"),
        # Logging settings
        ("logbook", "logging.log_path"),
        # Display settings
        ("no_weekly", "display.calculate_weekly_hours"),
        ("no_overhours", "display.calculate_daily_overhours"),
        ("tail", "display.show_tail"),
    ]

    def _set_nested_value(config_dict: dict, path: str, value: str | int | bool) -> None:  # noqa: FBT001
        """Set a value in a nested dictionary using dot notation."""
        keys = path.split(".")
        current = config_dict

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            current = current.setdefault(key, {})

        # Set the final value
        current[keys[-1]] = value

    # Process each argument mapping
    for arg_name, config_path in arg_mappings:
        if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
            value = getattr(args, arg_name)

            _set_nested_value(updated_config, config_path, value)

    logger.debug("Configuration updated with command line arguments")
    return updated_config

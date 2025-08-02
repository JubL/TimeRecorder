"""
Configuration utilities for the TimeRecorder project.

This module provides functionality to load and parse YAML configuration files,
with support for default values and configuration validation.
"""

import pathlib

import yaml

from src.logging_utils import setup_logger

# Set up logger
logger = setup_logger(__name__)


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
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with config_path.open(encoding="utf-8") as file:
            config = yaml.safe_load(file)
        logger.debug(f"Configuration loaded from {config_path}")
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {config_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration file {config_path}: {e}")
        raise


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

    return {
        "date": time_tracking.get("date", "01.08.2025"),
        "start_time": time_tracking.get("start_time", "07:00"),
        "end_time": time_tracking.get("end_time", "17:25"),
        "lunch_break_duration": time_tracking.get("lunch_break_duration", 60),
        "full_format": time_tracking.get("full_format", "%d.%m.%Y %H:%M:%S"),
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

    return {
        "log_path": pathlib.Path.cwd() / logging_config.get("log_path", "timereport_logbook.txt"),
        "full_format": config.get("time_tracking", {}).get("full_format", "%d.%m.%Y %H:%M:%S"),
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
    logging_config = config.get("logging", {})

    return {
        "use_boot_time": config.get("time_tracking", {}).get("use_boot_time", True),
        "log_enabled": logging_config.get("enabled", False),
        "auto_squash": data_processing.get("auto_squash", True),
        "add_missing_days": data_processing.get("add_missing_days", True),
        "calculate_weekly_hours": data_processing.get("calculate_weekly_hours", True),
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
            logger.error(f"Missing required configuration section: {section}")
            return False

    # Validate time tracking settings
    time_tracking = config.get("time_tracking", {})
    required_time_fields = ["date", "start_time", "end_time", "lunch_break_duration"]

    for field in required_time_fields:
        if field not in time_tracking:
            logger.error(f"Missing required time tracking field: {field}")
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
    """
    if config_path.exists():
        logger.debug(f"Configuration file already exists: {config_path}")
        return

    default_config: dict = {
        "time_tracking": {
            "use_boot_time": True,
            "date": "01.08.2025",
            "start_time": "07:30",
            "end_time": "17:25",
            "lunch_break_duration": 60,
            "full_format": "%d.%m.%Y %H:%M:%S",
        },
        "logging": {
            "enabled": False,
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
            "include_holidays": True,
        },
        "data_processing": {
            "auto_squash": True,
            "add_missing_days": True,
            "calculate_weekly_hours": True,
        },
        "output": {
            "colored_output": True,
            "show_statistics": True,
            "export_format": "csv",
        },
    }

    try:
        with config_path.open("w", encoding="utf-8") as file:
            yaml.dump(default_config, file, default_flow_style=False, sort_keys=False)
        logger.debug(f"Default configuration file created: {config_path}")
    except yaml.YAMLError as e:
        logger.error(f"Error creating default configuration file: {e}")
        raise

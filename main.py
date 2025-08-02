#!/usr/bin/env python3
"""
Main module for the time_recorder project.

Provides a main function that creates a TimeRecorder object and a Logbook object,
and uses them to record the time and log the results.
"""

import logging
import pathlib

from src.config_utils import (
    create_default_config,
    get_logbook_config,
    get_processing_config,
    get_time_recorder_config,
    load_config,
    validate_config,
)
from src.logbook import Logbook
from src.logging_utils import set_global_log_level, setup_logger
from src.time_recorder import TimeRecorder

# Set global log level first (change this to control all logging)
# Options: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
set_global_log_level(logging.INFO)

# Set up main logger
logger = setup_logger(__name__)


def main() -> None:
    """Run the main function of the time recorder."""
    # TODO: use argparse to parse the command line arguments
    # TODO: if only the end time is given, then the start time is the boot time, etc.

    # TODO: increase the test coverage to 100%

    # TODO: introduce integration tests

    # TODO: tidy up duplicate code in squash_df method of Logbook class

    # TODO: squash_df needs to identifiy duplicate entries and not squash those together

    # TODO: add timezones to the logged time?

    # TODO: improve the documentation

    # TODO: add_missing_days shall add missing days that are not weekend days nor holidays in a specific format
    # TODO: (e.g. Mon;30.06.2025;cluster meeting MNR;;;;;) -> (weekday;date;tag;;;;;)

    # TODO: introduce outlier detection, consistency checks?

    # TODO: visualization of work hours per day, week, month, year

    # TODO: calc overtime mean and std dev

    # TODO: have the option to set the end time to now + 1 minute

    # TODO: introduce logbook.tail()

    # TODO: split the test for config_utils in seperate files

    # Create default config if it doesn't exist
    config_path = pathlib.Path("config.yaml")
    if not config_path.exists():
        create_default_config(config_path)

    config = load_config(config_path)
    if not validate_config(config):
        logger.error("Configuration validation failed")
        return

    # Extract configuration sections
    time_recorder_config = get_time_recorder_config(config)
    logbook_config = get_logbook_config(config)
    processing_config = get_processing_config(config)
    logger.debug("Configuration loaded successfully")

    # Create TimeRecorder object from configuration
    tr_line = TimeRecorder.from_dict(time_recorder_config)
    logbook = Logbook(log_path=logbook_config["log_path"])

    # Process based on configuration
    if processing_config["use_boot_time"]:
        tr_line.update_boot_time()
        tr_line.get_state()

    if processing_config["log_enabled"]:
        logbook.record_into_df(tr_line.time_report_line_to_dict())

        if processing_config["add_missing_days"]:
            logbook.find_and_add_missing_days()

        if processing_config["auto_squash"]:
            logbook.squash_df()

    if processing_config["calculate_weekly_hours"]:
        logbook.get_weekly_hours_from_log()


if __name__ == "__main__":
    main()

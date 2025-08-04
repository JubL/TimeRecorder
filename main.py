#!/usr/bin/env python3
"""
Main module for the time_recorder project.

Provides a main function that creates a TimeRecorder object and a Logbook object,
and uses them to record the time and log the results.
"""

import logging
import pathlib

import src.arg_parser as ap
import src.config_utils as cu
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
    # TODO: increase the test coverage to 95%

    # TODO: introduce integration tests

    # TODO use zoneinfo package over pytz package
    # TODO: reactivate ruffs timezone checks
    # TODO: timezoned were added to the logged time, but they do not show up in the log yet (see line 377 in timerecorder.py)

    # TODO: visualization of work hours per day, week, month, year
    # TODO: calc overtime mean and std dev
    # TODO: introduce outlier detection, consistency checks?

    # TODO: have the option to set the end time to now + 1 minute

    # TODO: split the test for config_utils into separate files

    # TODO set up CI/CD workflows on GitHub

    # TODO: use dtype arg in read_csv?

    # TODO: use pytests approx to compare with float in unit tests, also set the precision to a small value, like 1e-9.

    # TODO: set up bash completion (https://docs.pytest.org/en/stable/how-to/bash-completion.html)

    # TODO: set up a launch.json for debugging and also for normal execution

    args = ap.run_arg_parser()

    # Create default config if it doesn't exist
    config_path = pathlib.Path(args.config or "config.yaml")
    if not config_path.exists():
        cu.create_default_config(config_path)

    config = cu.load_config(config_path)
    if not cu.validate_config(config):
        logger.error("Configuration validation failed")
        return

    # Update the config with the command line arguments
    config = cu.update_config(config, args)

    # Extract configuration sections
    time_recorder_config = cu.get_time_recorder_config(config)
    logbook_config = cu.get_logbook_config(config)
    processing_config = cu.get_processing_config(config)
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

    if processing_config["log_enabled"]:
        logbook.tail()


if __name__ == "__main__":
    main()

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
import src.logging_utils as lu
from src.logbook import Logbook
from src.time_recorder import TimeRecorder

# Set global log level first (change this to control all logging)
# Options: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
lu.set_global_log_level(logging.INFO)

# Set up main logger
logger = lu.setup_logger(__name__)


def main() -> None:
    """Run the main function of the time recorder."""
    # TODO: increase the test coverage to 95%

    # TODO: introduce integration tests

    # TODO: timezoned were added to the logged time, but they do not show up in the log yet (see line 377 in timerecorder.py)

    # TODO: visualization of work hours per day, week, month, year
    # TODO: calc overtime mean and std dev
    # TODO: introduce outlier detection, consistency checks?

    # TODO: set up bash completion (https://docs.pytest.org/en/stable/how-to/bash-completion.html)

    # TODO: set up a launch.json for debugging and also for normal execution?

    # TODO: executing test via the IDE does produce the german names of the holidays, but not when running the tests via pytest.

    # TODO: initialize logbook with its config? no
    # TODO: put the holidays into the logbook object

    # TODO: use log level from config.yaml. put the logger into the main?
    # TODO: use standard_work_hours from config.yaml in the timerecorder object
    # TODO: use work_days from config.yaml in the logbook class
    # TODO: use holidays from config.yaml in the logbook class

    # TODO: show averaged daily overtime in the terminal output next to the weekly work hours

    # TODO: add this weeks or last weeks average work hours and compare with the historic weekly work hours

    # TODO: lunch break duration in logbook is float again. change to int.

    # TODO: add the option to save and load the timereport_logbook in different formats, e.g. csv, json, yaml, parquet, etc.
    # TODO: add a method to determine the file format
    # TODO: make the load and save methods choose from a ariety of submethods, e.g. load_csv, load_parquet, etc

    # TODO: the output is diffrent from what is presented in README.md

    args = ap.run_arg_parser()

    # Create default config if it doesn't exist
    config_path = pathlib.Path(args.config or "config.yaml")
    if not config_path.exists():
        cu.create_default_config(config_path)

    config = cu.load_config(config_path)
    if not cu.validate_config(config):
        logger.error("Configuration validation failed")
        raise SystemExit(1)

    # Update the config with the command line arguments
    config = cu.update_config(config, args)

    # Extract configuration sections
    time_recorder_config = cu.get_time_recorder_config(config)
    logbook_config = cu.get_logbook_config(config)
    processing_config = cu.get_processing_config(config)
    display_config = cu.get_display_config(config)
    logger.debug("Configuration loaded successfully")

    # Create TimeRecorder object from configuration
    tr_line = TimeRecorder(time_recorder_config)
    logbook = Logbook(log_path=logbook_config["log_path"])

    # Process based on configuration
    if processing_config["use_boot_time"]:
        tr_line.update_boot_time()
        tr_line.print_state()

    if processing_config["log_enabled"]:
        tr_dict = tr_line.time_report_line_to_dict()
        logbook.record_into_df(tr_dict)

        if processing_config["add_missing_days"]:
            logbook.find_and_add_missing_days()

        if processing_config["auto_squash"]:
            logbook.squash_df()

    if processing_config["calculate_weekly_hours"]:
        logbook.get_weekly_hours_from_log()

    if processing_config["log_enabled"]:
        logbook.tail(display_config["show_tail"])


if __name__ == "__main__":
    main()

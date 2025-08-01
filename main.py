#!/usr/bin/env python3
"""
Main module for the time_recorder project.

Provides a main function that creates a TimeRecorder object and a Logbook object,
and uses them to record the time and log the results.
"""

import logging
import pathlib

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
    # TODO: or use a yaml config file

    # TODO: use a dict to store the parameters (the constants below) for the TimeRecorder object or perhaps a configuration file (yaml)

    # TODO: check the "--cov" flag of pytest in the pyproject.toml file

    # TODO: introduce a requirements.txt file?

    USE_BOOT_TIME = True  # Use system boot time as start time
    DATE = "25.07.2025"  # Date in DD.MM.YYYY format
    START_TIME = "07:00"  # Starting time in HH:MM format
    END_TIME = "17:25"  # Ending time in HH:MM format
    LUNCH_BREAK_DURATION = 60  # Duration of the lunch break in minutes
    LOG_PATH = pathlib.Path.cwd() / "timereport_logbook.txt"  # Path to the log file in the current directory
    LOG = False  # Set to True to log the results

    tr_line = TimeRecorder(date=DATE, start_time=START_TIME, end_time=END_TIME, lunch_break_duration=LUNCH_BREAK_DURATION)
    logbook = Logbook(log_path=LOG_PATH)

    if USE_BOOT_TIME:
        tr_line.update_boot_time()
        tr_line.get_state()
    if LOG:
        logbook.record_into_df(tr_line.time_report_line_to_dict())
        logbook.find_and_add_missing_days()
        logbook.squash_df()
    logbook.get_weekly_hours_from_log()


if __name__ == "__main__":
    main()

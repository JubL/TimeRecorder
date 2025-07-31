#!/usr/bin/env python3
"""
Main module for the time_recorder project.

Provides a main function that creates a TimeRecorder object and a Logbook object,
and uses them to record the time and log the results.
"""

import logging
import pathlib

from src.logbook import Logbook
from src.time_recorder import TimeRecorder

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # TODO: use argparse to parse the command line arguments
    # TODO: or use a yaml config file

    # TODO: squash_df logs a message everytime it is executed.
    # TODO: add a condition to indicate that squashing actually did occur

    # TODO: use a dict to store the parameters (the constants below) for the TimeRecorder object or perhaps a configuration file (yaml)

    # TODO: put the logging functionality into a seperate file / module

    # TODO: test whether the logging works with different log levels (are the logs propagated to the main module?)

    # TODO: put some test from squash_df.py into squash_df2.py

    # TODO: check the "--cov" flag of pytest in the pyproject.toml file

    # TODO: introduce a requirements.txt file?

    USE_BOOT_TIME = True  # Use system boot time as start time
    DATE = "25.07.2025"  # Date in DD.MM.YYYY format
    START_TIME = "07:00"  # Starting time in HH:MM format
    END_TIME = "17:15"  # Ending time in HH:MM format
    LUNCH_BREAK_DURATION = 60  # Duration of the lunch break in minutes
    LOG_PATH = pathlib.Path.cwd() / ".." / "timereport_logbook.txt"  # Path to the log file in the current directory
    LOG = False  # Set to True to log the results

    tr_line = TimeRecorder(date=DATE, start_time=START_TIME, end_time=END_TIME, lunch_break_duration=LUNCH_BREAK_DURATION)
    logbook = Logbook(log_path=LOG_PATH)

    if USE_BOOT_TIME:
        tr_line.update_boot_time()
    logger.info(tr_line)
    if LOG:
        logbook.record_into_df(tr_line.time_report_line_to_dict())
        logbook.find_and_add_missing_days()
        logbook.squash_df()
    average_weekly_hours = logbook.get_weekly_hours_from_log()
    logger.info(f"Average weekly hours: {average_weekly_hours} hours")

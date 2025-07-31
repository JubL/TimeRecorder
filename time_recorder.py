"""
Time recorder module for work hours calculation and evaluation.

This module provides comprehensive functionality for tracking and calculating work hours,
including overtime and undertime calculations based on start/end times and lunch breaks.
It supports system boot time integration for automatic start time detection and offers
detailed work hour analysis with colored terminal output.

Dependencies:
    - logging: For structured logging with level-specific formatting
    - pathlib: For file path operations
    - datetime, timedelta: For date/time manipulation and calculations
    - colorama: For colored terminal output (red/green for overtime/undertime)
    - psutil: For system boot time retrieval

Classes:
    TimeRecorder: Main class representing a single time report entry. Handles:
        - Work duration calculations (excluding lunch breaks)
        - Overtime/undertime determination (8-hour standard work day)
        - System boot time integration
        - Time parsing with automatic seconds handling
        - Data conversion for logbook storage
        - Formatted output with colored results

    BootTimeError: Custom exception raised when system boot time cannot be retrieved
        or processed correctly. Inherits from Exception.

    LevelSpecificFormatter: Custom logging formatter that provides different output
        formats for different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).

Key Features:
    - Automatic time format handling (adds seconds if missing)
    - System boot time integration for accurate start time detection
    - Comprehensive validation of time inputs and calculations
    - Colored output for overtime (green) and undertime (red)
    - Detailed logging with level-specific formatting
    - Data conversion for CSV logbook storage
"""

import logging
from datetime import datetime, timedelta

import colorama
import psutil


class LevelSpecificFormatter(logging.Formatter):
    """Custom formatter that provides different formats for different log levels."""

    def __init__(self) -> None:
        super().__init__()
        self.formatters = {
            logging.DEBUG: logging.Formatter(
                "%(levelname)s - %(funcName)s in line %(lineno)s - %(message)s",
            ),
            logging.INFO: logging.Formatter("%(message)s"),
            logging.WARNING: logging.Formatter(
                "%(levelname)s: %(message)s",
            ),
            logging.ERROR: logging.Formatter(
                "%(levelname)s: %(funcName)s - %(message)s",
            ),
            logging.CRITICAL: logging.Formatter(
                "%(levelname)s: %(funcName)s in %(filename)s:%(lineno)s - %(message)s",
            ),
        }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record using level-specific formatter."""
        formatter = self.formatters.get(record.levelno, self.formatters[logging.INFO])
        return formatter.format(record)


# Configure logging with custom formatter
handler = logging.StreamHandler()
handler.setFormatter(LevelSpecificFormatter())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False  # Prevent duplicate messages

colorama.init(autoreset=True)
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
RESET = colorama.Style.RESET_ALL


class BootTimeError(Exception):
    """Custom exception for errors retrieving boot time."""


class TimeRecorder:
    """
    Represents a line in the time report logbook.

    This class provides functionality to track and calculate work hours, including
    start and end times, lunch break duration, and overtime/undertime calculations.

    Attributes
    ----------
    weekday : str
        Abbreviation of the weekday (e.g., 'Mon', 'Tue', etc.).
    date : str
        The date of the record entry in format specified by date_format.
    start_time : datetime
        The starting time of work as a datetime object.
    end_time : datetime
        The ending time of work as a datetime object.
    lunch_break_duration : timedelta
        The duration of the lunch break.
    work_time : timedelta
        The total work duration excluding the lunch break.
    case : str
        The case indicating either 'overtime' or 'undertime'.
    overtime : timedelta
        The total amount of overtime or undertime as a timedelta object.
    full_format : str
        Format string for parsing full datetime (default: "%d.%m.%Y %H:%M:%S").
    date_format : str
        Format string for parsing date (default: "%d.%m.%Y").
    time_format : str
        Format string for parsing time (default: "%H:%M:%S").
    """

    def __init__(
        self,
        date: str,
        start_time: str,
        end_time: str,
        lunch_break_duration: int,
        full_format: str = r"%d.%m.%Y %H:%M:%S",
    ) -> None:
        """Initialize a TimeRecorder object with the provided parameters.

        Parameters
        ----------
        date : str
            Date in the format specified by date_format (default: "%d.%m.%Y").
        start_time : str
            Start time in the format specified by time_format (default: "%H:%M:%S").
        end_time : str
            End time in the format specified by time_format (default: "%H:%M:%S").
        lunch_break_duration : int
            Duration of the lunch break in minutes.
        full_format : str, optional
            Format string for parsing full datetime (default: "%d.%m.%Y %H:%M:%S").

        Notes
        -----
        - Time strings without seconds will have ":00" appended automatically.
        """

        def _parse_datetime(date: str, time: str, full_format: str) -> datetime:
            """
            Parse a datetime string, handling cases where seconds are missing.

            Parameters
            ----------
            date : str
                Date string in the format specified by date_format.
            time : str
                Time string, which may or may not include seconds.
            full_format : str
                The expected format string for the complete datetime.

            Returns
            -------
            datetime
                A datetime object parsed from the input strings.

            Notes
            -----
            If the time string doesn't include seconds (contains only one ':'),
            they will be added as ":00" before parsing.
            """
            # Check if time string has seconds (contains ':')
            if time.count(":") == 1:
                # Add seconds if missing
                time += ":00"

            try:
                return datetime.strptime(date + " " + time, full_format)
            except ValueError as e:
                raise ValueError(
                    f"{RED}Failed to parse datetime from date='{date}' and time='{time}' using format '{full_format}': {e}{RESET}",
                ) from e

        self.full_format = full_format
        self.date_format, self.time_format = self.full_format.split(" ")

        self.date = date

        self.start_time = _parse_datetime(date, start_time, full_format)  # Start time as a datetime object
        self.end_time = _parse_datetime(date, end_time, full_format)  # End time as a datetime object
        self.lunch_break_duration = timedelta(minutes=lunch_break_duration)  # Duration of the lunch break in minutes

        self.weekday = self.start_time.strftime("%a")

        self.evaluate_work_hours()

        self.sec_in_min = 60  # Number of seconds in a minute
        self.sec_in_hour = 3600  # Number of seconds in an hour
        self.min_in_hour = 60  # Number of minutes in an hour

    def update_boot_time(self) -> None:
        """Update the start time to the system boot time.

        This method retrieves the system boot time using psutil and updates
        the object's start_time attribute. The end_time is adjusted to match
        the boot time date while keeping its original time component.

        Raises
        ------
        BootTimeError
            If there is an error retrieving the boot time or processing the datetime values.

        Notes
        -----
        - Uses psutil.boot_time() to get the system boot time
        - Preserves the original time component of end_time while matching boot time date
        - Recalculates work hours and overtime after updating the times
        """
        try:
            # Get system boot time
            boot_timestamp = psutil.boot_time()
        except psutil.Error as e:
            raise BootTimeError(f"{RED}Error accessing system information: {e}{RESET}") from e

        # Update start time to boot time
        self.start_time = datetime.fromtimestamp(boot_timestamp)

        # get the function name and additional debug information
        logger.debug(f"Updated start_time to boot time: {self.start_time}")

        # Adjust end time to match boot time date while keeping original time
        try:
            self.end_time = datetime.strptime(
                self.start_time.date().strftime(self.date_format) + " " + self.end_time.strftime(self.time_format),
                self.full_format,
            )
        except ValueError as e:
            raise BootTimeError(f"{RED}Failed to adjust end time: {e}{RESET}") from e

        # Recalculate work hours
        self.evaluate_work_hours()

        # reset the date and the weekday
        self.date = self.start_time.date().strftime(self.date_format)
        self.weekday = datetime.strptime(self.date, self.date_format).strftime("%a")

    def evaluate_work_hours(self) -> None:
        """Evaluate the total work hours and calculate overtime/undertime.

        This method:
        1. Calculates total work duration excluding lunch break
        2. Calculates the overtime/undertime amount
        3. Determines if overtime or undertime was worked

        Notes
        -----
        Updates the following attributes:
        - work_time
        - case ('overtime' or 'undertime')
        - overtime
        """
        self.work_time = self.calculate_work_duration()
        self.case, self.overtime = self.calculate_overtime(self.work_time)

        logger.debug(f"Calculated work_time: {self.work_time}")
        logger.debug(f"Case: {self.case}, Overtime: {self.overtime}")

    def calculate_work_duration(self) -> timedelta:
        """Calculate the work duration by subtracting lunch break from total time between start and end.

        Returns
        -------
        timedelta
            The work duration excluding the lunch break.

        Raises
        ------
        ValueError
            If start time is not before end time,
            if lunch break duration is negative,
            or if calculated work duration is negative.
        """
        # Validate that start time is not after end time
        if self.start_time >= self.end_time:
            raise ValueError(
                f"{RED}The start time must be before the end time. Start time: {self.start_time}, End time: {self.end_time}{RESET}",
            )

        if self.lunch_break_duration < timedelta(0):
            raise ValueError(
                f"{RED}The lunch break duration must be a non-negative integer. Lunch break duration: {self.lunch_break_duration}{RESET}",
            )

        # Calculate the total duration between start and end times
        total_duration = self.end_time - self.start_time

        work_duration = total_duration - self.lunch_break_duration

        # Sanity check: work duration must not be negative
        if work_duration <= timedelta(0):
            raise ValueError(f"{RED}The work duration must be positive. Start time: {self.start_time}, End time: {self.end_time}{RESET}")

        logger.debug(f"Total duration: {total_duration}, Lunch break: {self.lunch_break_duration}, Work duration: {work_duration}")

        return work_duration

    @staticmethod
    def calculate_overtime(work_time: timedelta) -> tuple[str, timedelta]:
        """Determine whether the given work time results in overtime or undertime by comparing it to a full work day.

        A full work day is defined as 8 hours.

        Parameters
        ----------
        work_time : timedelta, default 0
            The total work time represented as a timedelta object.

        Returns
        -------
        tuple[str, timedelta]
            A tuple containing:
            - str: Case indicating 'overtime' or 'undertime'
            - timedelta: The amount of overtime or undertime calculated as a difference from a full work day
        """
        _full_day = timedelta(hours=8, minutes=0)

        if work_time >= _full_day:
            case = "overtime"
            overtime = work_time - _full_day
        else:
            case = "undertime"
            overtime = _full_day - work_time

        return case, overtime

    def time_report_line_to_dict(self) -> dict:
        """Convert a TimeRecorder object into a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the TimeRecorder object.
        """
        return {
            "weekday": self.weekday,
            "date": self.date,
            "start_time": self.start_time.strftime(self.time_format),
            "end_time": self.end_time.strftime(self.time_format),
            "lunch_break_duration": int(self.lunch_break_duration.total_seconds() // self.sec_in_min),
            "work_time": round(self.work_time.total_seconds() / self.sec_in_hour, 2),
            "case": self.case,
            "overtime": round(self.overtime.total_seconds() / self.sec_in_hour, 2),
        }

    def __repr__(self) -> str:
        """Return a string representation of the TimeRecorder object.

        Returns
        -------
        str
            A semicolon-separated string containing all relevant attributes of the object.
        """
        return (
            f"{self.weekday}; {self.date}; {self.start_time.strftime(self.time_format)}; "
            f"{self.end_time.strftime(self.time_format)}; {int(self.lunch_break_duration.total_seconds() // self.sec_in_min)}; "
            f"{self.work_time.total_seconds() // self.sec_in_hour}; "
            f"{self.work_time.total_seconds() // self.sec_in_min % self.min_in_hour}; "
            f"{self.case}; {self.overtime.total_seconds() // self.sec_in_hour}; "
            f"{self.overtime.total_seconds() // self.sec_in_min % self.min_in_hour}"
        )

    def __str__(self) -> str:
        """Return a formatted string representation of work duration and overtime information.

        Returns
        -------
        str
            A multi-line string containing:
            - Total work duration in hours and minutes
            - Total overtime/undertime amount
            - Decimal representation of overtime/undertime

        Raises
        ------
        ValueError
            If self.case is not 'overtime' or 'undertime'.

        Notes
        -----
        Overtime is displayed in green, undertime in red.
        """
        # Validate case value
        if self.case not in {"overtime", "undertime"}:
            raise ValueError(f"{RED}Unexpected value for case: {self.case}. Expected 'overtime' or 'undertime'.{RESET}")

        # Build output strings
        work_hours = int(self.work_time.total_seconds() // self.sec_in_hour)
        work_minutes = int(self.work_time.total_seconds() // self.sec_in_min % self.min_in_hour)
        work_hours_decimal_representation = round(self.work_time.total_seconds() / self.sec_in_hour, 2)
        overtime_hours = int(self.overtime.total_seconds() // self.sec_in_hour)
        overtime_minutes = int(self.overtime.total_seconds() // self.sec_in_min % self.min_in_hour)
        overtime_decimal_representation = round(self.overtime.total_seconds() / self.sec_in_hour, 2)

        work_duration = f"Total work duration: {work_hours} hours and {work_minutes} minutes ({work_hours_decimal_representation})."
        overtime_amount = f"Total {self.case}: {overtime_hours} hours and {overtime_minutes} minutes."

        color = GREEN if self.case == "overtime" else RED
        decimal_str = f"Decimal representation of {color}{self.case}{RESET} is {overtime_decimal_representation}."

        # Combine all parts
        return work_duration + "\n" + overtime_amount + "\n" + decimal_str

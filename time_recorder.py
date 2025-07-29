#!/usr/bin/env python3
"""
Work Hours Evaluation and Logging Module.

This module provides functionality to calculate and evaluate work hours,
taking into account start and end times, lunch break duration, and optional
use of the system boot time as the starting point. It assesses whether the
work duration exceeds or falls short of a standard work day, calculates
possible overtime or undertime, and weekly work hour analysis.

Dependencies:
-------------
- logging: For logging messages and information.
- pathlib: For file path manipulations.
- datetime, timedelta: For manipulating dates and times.
- colorama: For colored terminal text output.
- pandas: For handling tabular data (CSV logbook).
- psutil: For retrieving system boot time.
- holidays: (optional, commented out) For handling public holidays.

Classes:
--------
- TimeRecorder: Represents a single time report entry and provides methods for work hour calculations and logbook management.
- BootTimeError: Custom exception for boot time retrieval errors.

Functions:
----------
calculate_work_duration(_start_time: datetime, _end_time: datetime, _lunch_break_duration: int) -> timedelta
    Calculate work duration excluding lunch break.

get_boot_time(time_format: str) -> datetime
    Retrieve system boot time.

evaluate_work_hours(_use_boot_time: bool, _start_time: str, _end_time: str, _lunch_break_duration: int, _format: str) -> tuple[int, int, str, int, int]
    Evaluate work hours and calculate overtime or undertime.

calculate_overtime(work_time: timedelta) -> tuple[str, timedelta]
    Determine overtime or undertime based on work duration.

record_into_logbook(_weekday: str, _date: str, _start_time: str, _end_time: str, _lunch_break_duration: int, _work_hours: int,
                    _work_minutes: int, _case: str, _overtime_hours: int, _overtime_minutes: int, filename: str) -> None
    Append a new record to the logbook CSV file.

display_results(_work_hours: int, _work_minutes: int, _case: str, _overtime_hours: int, _overtime_minutes: int) -> None
    Display formatted work duration and overtime / undertime information.

main(use_boot_time: bool, date: str, start_time: str, end_time: str, lunch_break_duration: int, log: bool, log_path: str) -> None
    Main function to calculate work hours and write a log entry if logging is enabled.

Logbook File Format:
--------------------
CSV file with columns:
    weekday, date, start_time, end_time, lunch_break_duration, work_time, case, overtime

Script Usage:
-------------
If called as a standalone script, it will calculate work hours and print
results based on the defined start and end times, lunch break, and utilizing
the system boot time as the starting point if enabled.

"""
import logging
import pathlib
from datetime import datetime, timedelta

import colorama
import holidays
import pandas as pd
import psutil

# logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(funcName)s in line %(lineno)s - %(message)s")  # noqa
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

colorama.init(autoreset=True)
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
RESET = colorama.Style.RESET_ALL

holidays_de_he = holidays.country_holidays("DE", subdiv="HE")


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
        self, date: str, start_time: str, end_time: str, lunch_break_duration: int, full_format: str = r"%d.%m.%Y %H:%M:%S"
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
                    f"{RED}Failed to parse datetime from date='{date}' and time='{time}' using format '{full_format}': {e}{RESET}"
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
                self.start_time.date().strftime(self.date_format) + " " + self.end_time.strftime(self.time_format), self.full_format
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
        self.case, self.overtime = self.calculate_overtime()

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
                f"{RED}The start time must be before the end time. Start time: {self.start_time}, End time: {self.end_time}{RESET}"
            )

        if self.lunch_break_duration < timedelta(0):
            raise ValueError(
                f"{RED}The lunch break duration must be a non-negative integer. Lunch break duration: {self.lunch_break_duration}{RESET}"
            )

        # Calculate the total duration between start and end times
        total_duration = self.end_time - self.start_time

        work_duration = total_duration - self.lunch_break_duration

        # Sanity check: work duration must not be negative
        if work_duration <= timedelta(0):
            raise ValueError(f"{RED}The work duration must be positive. Start time: {self.start_time}, End time: {self.end_time}{RESET}")

        logger.debug(f"Total duration: {total_duration}, Lunch break: {self.lunch_break_duration}, Work duration: {work_duration}")

        return work_duration

    def calculate_overtime(self, work_time: timedelta | None = None) -> tuple[str, timedelta]:
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

        if work_time is None:
            # If no work_time is provided, use the instance's work_time attribute
            work_time = self.work_time

        if work_time >= _full_day:
            case = "overtime"
            overtime = work_time - _full_day
        else:
            case = "undertime"
            overtime = _full_day - work_time

        return case, overtime

    def load_logbook(self, log_path: pathlib.Path) -> pd.DataFrame:
        """Load the logbook CSV file into a pandas DataFrame.

        Parameters
        ----------
        log_path : pathlib.Path
            Path to the logbook CSV file.

        Returns
        -------
        pd.DataFrame
            The loaded DataFrame containing the logbook data.

        Notes
        -----
        If the logbook file does not exist or is empty, a new DataFrame is created.
        Handles file not found, empty data, and parsing errors gracefully.
        """
        if not log_path.exists() or log_path.stat().st_size == 0:
            self.create_df(log_path)

        try:
            df = pd.read_csv(log_path, sep=";", encoding="utf-8")  # how are empty fields read? as NaN?
            logger.debug(f"Read logbook from {log_path}")
        except FileNotFoundError:
            logger.exception(f"{RED}Log file not found: {log_path}{RESET}")
        except pd.errors.EmptyDataError:
            logger.exception(f"{RED}Log file is empty: {log_path}{RESET}")
        except pd.errors.ParserError as e:
            logger.exception(f"{RED}Error parsing log file: {e}{RESET}")

        # sanity checks
        # make sure all required coloumns are present
        required_columns = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
        if not all(col in df.columns for col in required_columns):
            raise KeyError(f"{RED}Log file is missing required columns: {required_columns}.")

        # count the number of coloumns
        if len(df.columns) != len(required_columns):
            raise ValueError(f"{RED}Log file has an unexpected number of columns: {len(df.columns)}. Expected 8 columns.{RESET}")

        # TODO: Check if the columns are in the correct format (e.g., date as datetime, time as str)

        return df

    def save_logbook(self, df: pd.DataFrame, log_path: pathlib.Path) -> None:
        """Save a pandas DataFrame to a CSV file.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to be saved.
        log_path : pathlib.Path
            Path to the CSV file.

        Notes
        -----
        The DataFrame is saved using ';' as the separator and UTF-8 encoding.
        Handles OSError and general exceptions gracefully.
        """
        if len(df) > 0 and type(df["date"][0]) is pd.Timestamp:
            # Convert 'date' column to string format if it is in datetime format
            df["date"] = df["date"].dt.strftime(self.date_format)
        try:
            df.to_csv(log_path, sep=";", index=False, encoding="utf-8")
            logger.debug(f"Logbook saved to {log_path}")
        except PermissionError as e:
            logger.exception(f"{RED}Permission denied when saving logbook to {log_path}: {e}{RESET}")
        except OSError as e:
            logger.exception(f"{RED}OS error while saving logbook to {log_path}: {e}{RESET}")
        except Exception as e:
            logger.exception(f"{RED}Unexpected error saving logbook to {log_path}: {e}{RESET}")

    def record_into_df(self, df_path: pathlib.Path) -> None:
        """Write the time report data into a pandas dataframe.

        Parameters
        ----------
        df_path : pathlib.Path
            Path to the pandas dataframe file.

        Raises
        ------
        OSError
            If the pandas dataframe directory does not exist.
        """
        # Ensure the directory exists and create a new DataFrame if it doesn't

        df = self.load_logbook(df_path)

        # Add the new row to the DataFrame in a single line
        df.loc[len(df)] = self.time_report_line_to_dict()
        self.save_logbook(df, df_path)

    def create_df(self, df_path: pathlib.Path) -> None:
        """Create a pandas dataframe file.

        Parameters
        ----------
        df_path : pathlib.Path
            Path to the pandas dataframe file.
        """
        # create a pandas dataframe
        columns = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
        df = pd.DataFrame(columns=columns)
        self.save_logbook(df, df_path)

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

    def squash_df(self, df_path: pathlib.Path) -> None:
        """Squash the DataFrame by grouping entries by date and summing work hours.

        This method reads a CSV file, groups the entries by date, and sums the work hours for each date.
        The result is saved back to the same CSV file.

        Parameters
        ----------
        df_path : pathlib.Path
            Path to the pandas dataframe file.
        """

        def calculate_total_overtime(row: pd.Series) -> float | str:
            """
            Calculate total overtime for a given row.

            Return empty string if work_time is missing or empty, otherwise calculate overtime.
            """
            if not row["work_time"] or pd.isnull(row["work_time"]):
                return ""
            # Overtime is total work_time minus 8 hours (per day)
            overtime = row["work_time"] - 8
            return round(overtime, 2)

        def reevaluate_case(row: pd.Series) -> str:
            """Reevaluate the case based on the work_time."""
            if not row["work_time"] or pd.isnull(row["work_time"]):
                return ""
            # work_time is in hours (float)
            work_time_td = timedelta(hours=row["work_time"]) if row["work_time"] else timedelta(0)
            case, _ = self.calculate_overtime(work_time_td)
            return case

        df = self.load_logbook(df_path)
        df["date"] = pd.to_datetime(df["date"], format=self.date_format)

        # Group by date and weekday, aggregate work_time and lunch_break_duration
        df = (
            df.groupby(["date", "weekday"], as_index=False)
            .agg(
                {
                    "start_time": "first",
                    "end_time": "last",
                    "lunch_break_duration": lambda x: x.sum() if x.notnull().any() else "",
                    "work_time": lambda x: x.sum() if x.notnull().any() else "",
                }
            )
            .reset_index(drop=True)
        )

        df["case"] = df.apply(reevaluate_case, axis=1)
        df["overtime"] = df.apply(calculate_total_overtime, axis=1)

        # Reorder columns so 'weekday' comes before 'date'
        columns_order = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
        # Format 'date' column according to self.date_format
        df["date"] = df["date"].dt.strftime(self.date_format)
        df = df[columns_order]
        self.save_logbook(df, df_path)

    def find_and_add_missing_days(self, log_path: pathlib.Path) -> None:
        """Find and add missing holidays and weekend days to the log file.

        This method checks the log file for missing entries.
        If these days are missing, it adds them with just the weekday and the date.

        Parameters
        ----------
        log_path : pathlib.Path
            The file path to the CSV log file. The file must contain a 'date' column.
        """
        missing_days = self.find_missing_days_in_logbook(log_path)

        if missing_days:
            self.add_missing_days_to_logbook(missing_days, log_path)

    def find_missing_days_in_logbook(self, log_path: pathlib.Path) -> list[tuple[datetime, datetime]]:
        """Find missing days in the logbook by checking for gaps between consecutive entries.

        This method loads the logbook CSV file, checks for any missing days between consecutive entries,
        and returns a list of tuples representing the start and end dates of the missing periods.

        Parameters
        ----------
        log_path : pathlib.Path
            The file path to the CSV log file. The file must contain a 'date' column.

        Returns
        -------
        list[tuple[datetime, datetime]]
            A list of tuples, where each tuple contains the start and end dates of a missing period.

        Notes
        -----
        - If the log file is empty, it logs a warning and returns an empty list.
        - If there are missing days, it logs a warning for each gap found.
        """
        df = self.load_logbook(log_path)

        if df.empty:
            logger.warning(f"{RED}Log file is empty. Cannot add weekend days.{RESET}")
            return []

        df["date"] = pd.to_datetime(df["date"], format=self.date_format)

        # Check the log for any missing days
        # a day is missing if two consecutive entries are not consecutive days
        missing_days = []
        for i in range(len(df) - 1):
            if (df["date"].iloc[i + 1] - df["date"].iloc[i]).days > 1:
                logger.warning(
                    f"{RED}There are missing days in the logbook between {df['date'].iloc[i].strftime(self.date_format)} "
                    f"and {df['date'].iloc[i + 1].strftime(self.date_format)}{RESET}"
                )
                missing_days.append((df["date"].iloc[i], df["date"].iloc[i + 1]))

        return missing_days

    def add_missing_days_to_logbook(self, missing_days: list[tuple[datetime, datetime]], log_path: pathlib.Path) -> None:
        """Add missing Saturdays, Sundays, and holidays to the logbook DataFrame for specified date ranges.

        For each tuple of (start_date, end_date) in `missing_days`, this method generates all dates between the two (excluding the endpoints),
        and checks if each date is missing from the logbook. If a date is a holiday (as defined in `holidays_de_he`), Saturday, or Sunday,
        and is not already present in the DataFrame, it is added with appropriate default values.
        After processing, the DataFrame is sorted by date and saved back to the specified log file.

        Parameters
        ----------
        df: pd.DataFrame
            The logbook DataFrame to update. Must contain a 'date' column.
        missing_days: list of tuple of datetime
            List of (start_date, end_date) tuples specifying date ranges to check for missing days.
        log_path: pathlib.Path
            Path to the logbook file where the updated DataFrame will be saved.

        Returns
        -------
        None
        """
        df = self.load_logbook(log_path)
        # Convert 'date' column to string format for comparison
        df["date"] = pd.to_datetime(df["date"], format=self.date_format).dt.strftime(self.date_format)

        saturday = 5  # Constant for Saturday
        sunday = 6  # Constant for Sunday

        for start_date, end_date in missing_days:
            # Generate all dates between start_date and end_date (exclusive)
            all_dates = pd.date_range(start=start_date + timedelta(days=1), end=end_date - timedelta(days=1), freq="D")
            for date in all_dates:
                date_str = date.strftime(self.date_format)
                if any(df["date"] == date_str):
                    continue

                if date in holidays_de_he:
                    logger.info(f"Found a wild {holidays_de_he[date]}.")  # Print the name of the holiday.
                    df.loc[len(df)] = {
                        "weekday": date.strftime("%a"),
                        "date": date_str,
                        "start_time": holidays_de_he[date],
                        "end_time": "",
                        "lunch_break_duration": "",
                        "work_time": "",
                        "case": "",
                        "overtime": "",
                    }
                    logger.info(f"Added missing holiday on {date_str} - {holidays_de_he[date]}")

                if date.weekday() == saturday and not any(df["date"] == date_str):
                    df.loc[len(df)] = {
                        "weekday": "Sat",
                        "date": date_str,
                        "start_time": "",
                        "end_time": "",
                        "lunch_break_duration": "",
                        "work_time": "",
                        "case": "",
                        "overtime": "",
                    }
                    logger.info(f"Added missing Saturday on {date_str}")
                elif date.weekday() == sunday and not any(df["date"] == date_str):
                    df.loc[len(df)] = {
                        "weekday": "Sun",
                        "date": date_str,
                        "start_time": "",
                        "end_time": "",
                        "lunch_break_duration": "",
                        "work_time": "",
                        "case": "",
                        "overtime": "",
                    }
                    logger.info(f"Added missing Sunday on {date_str}")

        # Sort and save the updated DataFrame back to the log file
        df.sort_values(by="date", inplace=True, key=lambda x: pd.to_datetime(x, format=self.date_format))
        self.save_logbook(df, log_path)

    def get_weekly_hours_from_log(self, log_path: pathlib.Path) -> float:
        """Calculate the averaged weekly work hours from a log file.

        This method reads a CSV log file containing daily work times, computes the average work hours per day
        (considering only days with recorded work time), and extrapolates this average to a standard 5-day work week.

        Parameters
        ----------
        log_path : pathlib.Path
            The file path to the CSV log file. The file must contain a 'work_time' column (in hours) and a 'date' column.

        Returns
        -------
        float
            The estimated total work hours for a standard 5-day week, rounded to two decimal places.
            Returns 0.0 if no work days are found in the log file.
        """
        result = 0.0

        df = self.load_logbook(log_path)

        try:
            df["work_time"] = pd.to_timedelta(df["work_time"], unit="h")
        except (ValueError, TypeError) as e:
            logger.exception(f"{RED}Error converting 'work_time' to timedelta: {e}{RESET}")
        else:
            weekly_hours = df["work_time"].sum().total_seconds() / self.sec_in_hour
            num_days = df[df["work_time"] > pd.Timedelta(0)]["date"].nunique()
            logger.debug(f"Weekly hours: {weekly_hours}, Number of days: {num_days}")
            if num_days == 0:
                logger.warning("No work days found in the log file.")
            else:
                weekly_hours /= num_days  # average work hours per day
                weekly_hours *= 5  # assuming a 5-day work week
                result = round(weekly_hours, 2)
        return result

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
            f"{self.work_time.total_seconds() // self.sec_in_hour}; {self.work_time.total_seconds() // self.sec_in_min % self.min_in_hour}; "
            f"{self.case}; {self.overtime.total_seconds() // self.sec_in_hour}; {self.overtime.total_seconds() // self.sec_in_min % self.min_in_hour}"
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


if __name__ == "__main__":
    # TODO: maybe use command line arguments for the use_boot_time, date, start time, end time, lunch break duration and logging and log path
    # TODO: use argparse to parse the command line arguments
    # TODO: or use a yaml config file

    # TODO: add a log message to squash_df to indicate that squashing did occure

    # TODO: put logbook handling into a separate class
    # TODO: put the test of one class into one file or folder and the test of another class into another file or folder

    # TODO: write tests for load_logbook, save_logbook, create_df, find_missing_days_in_logbook, add_missing_days_to_logbook

    # TODO: use a dict to store the parameters for the TimeRecorder object or perhaps a configuration file (yaml)

    # TODO: configure logging so that the messages format is diffrent for info and debug levels

    USE_BOOT_TIME = True  # Use system boot time as start time
    DATE = "25.07.2025"  # Date in DD.MM.YYYY format
    START_TIME = "07:00"  # Starting time in HH:MM format
    END_TIME = "18:10"  # Ending time in HH:MM format
    LUNCH_BREAK_DURATION = 60  # Duration of the lunch break in minutes
    LOG_PATH = pathlib.Path.cwd() / "timereport_logbook.txt"  # Path to the log file in the current directory
    LOG = False  # Set to True to log the results

    # Create a TimeRecorder object with parameters
    tr_line = TimeRecorder(date=DATE, start_time=START_TIME, end_time=END_TIME, lunch_break_duration=LUNCH_BREAK_DURATION)

    if USE_BOOT_TIME:
        tr_line.update_boot_time()

    logger.info(tr_line)

    if LOG:
        tr_line.record_into_df(LOG_PATH)
        tr_line.find_and_add_missing_days(LOG_PATH)
        tr_line.squash_df(LOG_PATH)

    average_weekly_hours = tr_line.get_weekly_hours_from_log(LOG_PATH)
    logger.info(f"Average weekly hours: {average_weekly_hours} hours")

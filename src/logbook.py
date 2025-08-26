"""
Logbook module for managing work time records.

This module provides comprehensive functionality for managing CSV-based time tracking data.
The Logbook class handles all aspects of work time record management including data
loading, saving, validation, and processing operations.

Key Features:
    - CSV-based logbook file management with automatic creation
    - Duplicate detection and removal with detailed logging
    - Data squashing/aggregation by date with work hour calculations
    - Missing day detection and automatic weekend/holiday insertion
    - Weekly work hour calculations and overtime analysis
    - Comprehensive error handling and validation

Dependencies:
    - pandas: For DataFrame operations and CSV handling
    - pathlib: For file path operations
    - datetime, timedelta: For date/time calculations
    - colorama: For colored terminal output
    - holidays: For holiday detection (German Hesse region)
    - logging: For structured logging

Classes:
    Logbook: Main class for logbook management. Handles:
        - CSV file loading and saving with error handling
        - Data validation and integrity checks
        - Duplicate detection and removal
        - Data aggregation and squashing operations
        - Missing day detection and insertion
        - Weekly work hour calculations

File Format:
    The logbook uses CSV format with semicolon (;) separator and UTF-8 encoding.
    Required columns: weekday, date, start_time, end_time, lunch_break_duration,
    work_time, case, overtime.

Error Handling:
    - Graceful handling of missing files (creates new file)
    - Validation of required columns and data types
    - Detailed error messages with color coding
    - Non-blocking duplicate warnings
"""

import pathlib
from datetime import datetime, timedelta

import colorama
import holidays
import pandas as pd

import src.logging_utils as lu
from src import formats

# Set up logger with centralized configuration
logger = lu.setup_logger(__name__)

colorama.init(autoreset=True)
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
RESET = colorama.Style.RESET_ALL


class Logbook:
    """
    Represents a logbook of work hours with comprehensive data management capabilities.

    This class provides functionality to load, save, and manipulate a logbook of work hours.
    It handles CSV-based time tracking data with features for data validation, duplicate
    removal, aggregation, and analysis.

    Attributes
    ----------
    log_path : pathlib.Path
        Path to the logbook CSV file.
    full_format : str
        Format string for parsing full datetime (default: "%d.%m.%Y %H:%M:%S").
    date_format : str
        Format string for parsing date (default: "%d.%m.%Y").
    time_format : str
        Format string for parsing time (default: "%H:%M:%S").
    sec_in_min : int
        Number of seconds in a minute (60).
    sec_in_hour : int
        Number of seconds in an hour (3600).
    min_in_hour : int
        Number of minutes in an hour (60).

    Notes
    -----
    The logbook file uses CSV format with semicolon (;) separator and UTF-8 encoding.
    Required columns: weekday, date, start_time, end_time, lunch_break_duration,
    work_time, case, overtime.
    """

    def __init__(self, data: dict) -> None:
        """Initialize a Logbook object with the provided parameters.

        Parameters
        ----------
        log_path : pathlib.Path
            Path to the logbook file.
        full_format : str
            Format string for parsing full datetime (default: "%d.%m.%Y %H:%M:%S").
        """
        self.log_path = data["log_path"]
        self.full_format = data["full_format"]
        self.date_format, self.time_format = self.full_format.split(" ")

        self.sec_in_min = 60  # Number of seconds in a minute
        self.sec_in_hour = 3600  # Number of seconds in an hour
        self.min_in_hour = 60  # Number of minutes in an hour

        self.standard_work_hours = data["standard_work_hours"]
        self.work_days = data["work_days"]

        self.holidays_de_he = holidays.country_holidays(data["holidays"], subdiv=data["subdivision"], language="en")

    def load_logbook(self) -> pd.DataFrame:
        """Load the logbook file into a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            The loaded DataFrame containing the logbook data.

        Raises
        ------
        pandas.errors.EmptyDataError
            If the logbook file is empty and cannot be processed.
        pandas.errors.ParserError
            If the logbook file has parsing errors.
        FileNotFoundError
            If the logbook file does not exist and cannot be created.
        KeyError
            If the logbook file is missing required columns.
        ValueError
            If the logbook file has an unexpected number of columns.

        Notes
        -----
        If the logbook file does not exist or is empty, a new DataFrame is created.
        Handles file not found, empty data, and parsing errors gracefully.
        Automatically detects file format based on file extension.
        """
        # Get the appropriate format handler based on file extension
        format_handler = formats.get_format_handler(self.log_path)

        # If the logbook file doesn't exist or is empty, return an empty dataframe.
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            columns = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
            return pd.DataFrame(columns=columns)

        df = format_handler.load(self.log_path)
        msg = f"Read logbook from {self.log_path}"
        logger.debug(msg)

        # sanity checks
        # make sure all required columns are present
        required_columns = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
        if not all(col in df.columns for col in required_columns):
            msg = f"Log file is missing required columns: {required_columns}."
            raise KeyError(msg)

        # count the number of columns
        if len(df.columns) != len(required_columns):
            msg = f"{RED}Log file has an unexpected number of columns: {len(df.columns)}. Expected 8 columns.{RESET}"
            raise ValueError(msg)

        # Convert columns to their expected types after validation
        df["weekday"] = df["weekday"].astype("string")
        df["date"] = df["date"].astype("string")
        df["start_time"] = df["start_time"].astype("string")
        df["end_time"] = df["end_time"].astype("string")
        df["lunch_break_duration"] = pd.to_numeric(df["lunch_break_duration"], errors="coerce").fillna(0).astype(int)
        df["work_time"] = pd.to_numeric(df["work_time"], errors="coerce")
        df["case"] = df["case"].astype("string")
        df["overtime"] = pd.to_numeric(df["overtime"], errors="coerce").fillna("").astype("object")

        # case is one of three values
        if not all(df["case"].isin(["overtime", "undertime", ""])):
            msg = f"{RED}Log file has invalid case values: {df['case'].unique()}.{RESET}"
            raise ValueError(msg)

        return df

    def save_logbook(self, df: pd.DataFrame) -> None:
        """Save a pandas DataFrame to a file.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to be saved.

        Raises
        ------
        PermissionError
            If the logbook file cannot be saved due to permission issues.
        OSError
            If the logbook file cannot be saved due to OS errors.

        Notes
        -----
        The DataFrame is saved using the appropriate format handler based on file extension.
        Handles OSError and general exceptions gracefully.
        """
        if len(df) > 0 and type(df["date"][0]) is pd.Timestamp:
            # Convert 'date' column to string format if it is in datetime format
            df["date"] = df["date"].dt.strftime(self.date_format)

        # Get the appropriate format handler based on file extension
        format_handler = formats.get_format_handler(self.log_path)
        try:
            format_handler.save(df, self.log_path)
        except PermissionError as e:
            msg = f"Permission denied when saving logbook to {self.log_path}: {e}"
            raise PermissionError(msg) from e
        except OSError as e:
            msg = f"OS error while saving logbook to {self.log_path}: {e}"
            raise OSError(msg) from e

        msg = f"Logbook saved to {self.log_path}"
        logger.debug(msg)

    def record_into_df(self, data: dict) -> None:
        """
        Write the time report data into the logbook DataFrame.

        This method loads the current logbook, appends the new data as a row,
        and saves the updated DataFrame back to the CSV file.

        Parameters
        ----------
        data : dict
            The time report data to be written. Must contain all required columns:
            weekday, date, start_time, end_time, lunch_break_duration, work_time,
            case, overtime.

        Notes
        -----
        The data is appended as a new row to the existing logbook.
        The DataFrame is automatically saved after the operation.
        """
        df = self.load_logbook()
        df.loc[len(df)] = data
        self.save_logbook(df)

    @staticmethod
    def remove_duplicate_lines(df: pd.DataFrame) -> pd.DataFrame:
        """Remove exact duplicate rows from the logbook and log warnings about removed duplicates.

        This method identifies and removes rows that are exact duplicates (all columns match),
        keeping only the first occurrence of each duplicate set. It logs warnings about
        what was removed without raising an error.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to check for and remove duplicates from.

        Returns
        -------
        pd.DataFrame
            The DataFrame with duplicates removed.

        Notes
        -----
        - Uses pandas drop_duplicates() method to remove exact duplicates
        - Logs warnings for each set of duplicates removed
        - Does not raise exceptions, only logs warnings
        - Includes row indices and content in the warning messages for easier identification
        """
        if df.empty:
            return df

        # Find exact duplicates (all columns match) before removal
        duplicate_mask = df.duplicated(keep=False)
        duplicate_rows = df[duplicate_mask]

        if duplicate_rows.empty:
            return df

        # Group duplicates by their content to show them together
        duplicate_groups = df[duplicate_mask].groupby(df.columns.tolist()).apply(lambda x: x.index.tolist())

        # Log warnings for each set of duplicates
        for duplicate_content, row_indices in duplicate_groups.items():
            if len(row_indices) > 1:  # Only warn if there are actually duplicates
                # Convert the duplicate content tuple back to a dict for better formatting
                duplicate_dict = dict(zip(df.columns, duplicate_content, strict=False))

                # Keep the first occurrence, remove the rest
                rows_to_remove = row_indices[1:]  # All except the first

                msg = f"{RED}Removing {len(rows_to_remove)} duplicate(s) at row(s) {rows_to_remove}: {duplicate_dict}{RESET}"
                logger.warning(msg)

        # Remove duplicates, keeping the first occurrence
        return df.drop_duplicates(keep="first")

    def squash_df(self) -> None:
        """Squash the DataFrame by grouping entries by date and summing work hours.

        This method reads a CSV file, groups the entries by date, and sums the work hours for each date.
        The result is saved back to the same CSV file.

        """

        def calculate_overtime_from_work_time(work_time_val: float) -> tuple[str, float]:
            """
            Calculate overtime case and amount from work time in hours.

            Parameters
            ----------
            work_time_val : float
                Work time in hours

            Returns
            -------
            tuple[str, float]
                A tuple containing case ('overtime' or 'undertime') and overtime amount in hours
            """
            full_day_ = timedelta(hours=self.standard_work_hours)
            case = "overtime" if timedelta(hours=work_time_val) >= full_day_ else "undertime"

            overtime = timedelta(hours=work_time_val) - full_day_

            return case, round(overtime.total_seconds() / self.sec_in_hour, 2)

        def process_work_time_row(row: pd.Series) -> tuple[str, float | str]:
            """
            Process work time from a DataFrame row and return case and overtime.

            Parameters
            ----------
            row : pd.Series
                The row to process.

            Returns
            -------
            tuple[str, float | str]
                A tuple containing case ('overtime' or 'undertime') and overtime amount in hours

            Notes
            -----
            - Returns empty strings if work_time is missing or empty.
            """
            if not row["work_time"] or pd.isna(row["work_time"]):
                return "", ""

            # Convert work_time to float if it's a string
            work_time_val = float(row["work_time"]) if isinstance(row["work_time"], str) else row["work_time"]
            case, overtime = calculate_overtime_from_work_time(work_time_val)
            return case, overtime

        # Load original data to compare before and after squashing
        original_df = self.load_logbook()

        # Remove duplicate lines and get warnings about what was removed
        df_no_duplicates = self.remove_duplicate_lines(original_df)
        original_count = len(df_no_duplicates)

        df = df_no_duplicates.copy()
        df["date"] = pd.to_datetime(df["date"], format=self.date_format)

        # Group by date and weekday, aggregate work_time and lunch_break_duration
        df = (
            df.groupby(["date", "weekday"], as_index=False)
            .agg(
                {
                    "start_time": "first",
                    "end_time": "last",
                    "lunch_break_duration": lambda x: x.sum() if x.notna().any() else "",
                    "work_time": lambda x: x.sum() if x.notna().any() else 0,
                },
            )
            .reset_index(drop=True)
        )

        # Apply the unified processing function
        df[["case", "overtime"]] = df.apply(process_work_time_row, axis=1, result_type="expand")

        # Reorder columns so 'weekday' comes before 'date'
        columns_order = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
        # Format 'date' column according to self.date_format
        df["date"] = df["date"].dt.strftime(self.date_format)
        df = df[columns_order]

        # Check if squashing actually occurred (rows were reduced)
        squashed_count = len(df)
        squashing_occurred = squashed_count < original_count

        self.save_logbook(df)

        # Only log if squashing actually occurred
        if squashing_occurred:
            msg = f"{GREEN}Logbook squashed. {original_count - squashed_count} entries removed.{RESET}"
            logger.info(msg)

    def find_and_add_missing_days(self) -> None:
        """Find and add missing holidays and weekend days to the log file.

        This method checks the log file for missing entries.
        If these days are missing, it adds them with just the weekday and the date.

        Parameters
        ----------
        log_path : pathlib.Path
            The file path to the CSV log file. The file must contain a 'date' column.
        """
        gaps = self.find_missing_days_in_logbook()

        if gaps:
            self.add_missing_days_to_logbook(gaps)

    def find_missing_days_in_logbook(self) -> list[tuple[datetime, datetime]]:
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
        df = self.load_logbook()

        if df.empty:
            msg = f"{RED}Log file is empty. Cannot add weekend days.{RESET}"
            logger.warning(msg)
            return []

        df["date"] = pd.to_datetime(df["date"], format=self.date_format)

        # Check the log for any gaps between consecutive entries
        # a gap is missing if two consecutive entries are not consecutive days
        gaps = []
        for i in range(len(df) - 1):
            if (df["date"].iloc[i + 1] - df["date"].iloc[i]).days > 1:
                msg = f"{RED}There are gaps in the logbook between {df['date'].iloc[i].strftime(self.date_format)} "
                msg += f"and {df['date'].iloc[i + 1].strftime(self.date_format)}{RESET}"
                logger.warning(msg)
                gaps.append((df["date"].iloc[i], df["date"].iloc[i + 1]))

        return gaps

    def add_missing_days_to_logbook(self, gaps: list[tuple[datetime, datetime]]) -> None:
        """
        Add missing Saturdays, Sundays, and holidays to the logbook DataFrame for specified date ranges.

        For each tuple of (start_date, end_date) in `missing_days`, this method generates all dates between the two (excluding the
        endpoints), and checks if each date is missing from the logbook. If a date is a holiday (as defined in `holidays_de_he`),
        Saturday, or Sunday, and is not already present in the DataFrame, it is added with appropriate default values. After processing,
        the DataFrame is sorted by date and saved back to the specified log file.

        Parameters
        ----------
        df: pd.DataFrame
            The logbook DataFrame to update. Must contain a 'date' column.
        missing_days: list of tuple of datetime
            List of (start_date, end_date) tuples specifying date ranges to check for missing days.
        log_path: pathlib.Path
            Path to the logbook file where the updated DataFrame will be saved.

        Notes
        -----
        - The logbook DataFrame is updated in place.
        - The logbook DataFrame is sorted by date.
        """
        df = self.load_logbook()
        # Convert 'date' column to string format for comparison
        df["date"] = pd.to_datetime(df["date"], format=self.date_format).dt.strftime(self.date_format)

        friday = 4  # Constant for Friday

        for start_date, end_date in gaps:
            # Generate all dates between start_date and end_date (exclusive)
            all_dates = pd.date_range(start=start_date + timedelta(days=1), end=end_date - timedelta(days=1), freq="D")
            for date in all_dates:
                date_str = date.strftime(self.date_format)
                if any(df["date"] == date_str):
                    continue

                reason = ""
                if date.weekday() <= friday:
                    reason = "vacation"
                if date in self.holidays_de_he:
                    reason = self.holidays_de_he[date]
                    msg = f"Added missing holiday on {date_str} - {reason}"
                    logger.info(msg)

                df.loc[len(df)] = {
                    "weekday": date.strftime("%a"),
                    "date": date_str,
                    "start_time": reason,
                    "end_time": "",
                    "lunch_break_duration": "0",
                    "work_time": "0",
                    "case": "",
                    "overtime": "",
                }

            msg = f"Added {len(all_dates)} missing days to the logbook."
            logger.info(msg)

        # Sort and save the updated DataFrame back to the log file
        df = df.sort_values(by="date", key=lambda x: pd.to_datetime(x, format=self.date_format))
        self.save_logbook(df)

    def print_weekly_summary(self) -> None:
        """Get the weekly summary from the logbook."""
        weekly_hours, daily_overtime = self.get_weekly_hours_from_log()

        weekly_standard_hours = self.standard_work_hours * len(self.work_days)

        title = "\nWeekly Summary - Work Hours Calculator\n======================================"
        avr_weekly_hours = f"Average Weekly Hours: {int(weekly_hours)}h {int(weekly_hours % 1 * 60)}m"
        standard_hours_str = f"Standard Hours: {int(weekly_standard_hours)}h"
        if weekly_standard_hours % 1 != 0:
            standard_hours_str += f" {int(weekly_standard_hours % 1 * 60)}m"

        daily_overtime_str = f"Mean Daily Overtime: {int(daily_overtime)}h {int(daily_overtime % 1 * 60)}m"

        # Combine all parts
        items = [title, avr_weekly_hours, standard_hours_str, daily_overtime_str]
        logger.info("\n".join(items))

    def get_weekly_hours_from_log(self) -> tuple[float, float]:
        """
        Calculate the averaged weekly work hours from the logbook.

        This method reads the logbook file containing daily work times, computes the average work hours per day
        (considering only days with recorded work time), and extrapolates this average to a standard 5-day work week.

        Returns
        -------
        tuple[float, float]
            A tuple containing the average weekly work hours and the average daily overtime.

        Raises
        ------
        ValueError
            If the work_time column contains non-numeric values.

        Notes
        -----
        - Only considers days with work_time > 0 for averaging
        - Assumes a 5-day work week for extrapolation
        - Handles both numeric and string work_time values
        - Logs the result and any warnings about data quality
        - Returns 0.0 if no work days are found or if conversion errors occur
        """
        weekly_result: float = 0.0
        daily_result: float = 0.0

        df = self.load_logbook()

        try:
            # Convert work_time to timedelta, handling both numeric and string values
            # First, convert strings to numeric values where possible
            df["work_time"] = pd.to_numeric(df["work_time"], errors="coerce")
            df["overtime"] = pd.to_numeric(df["overtime"], errors="coerce")

            # Check if there are any NaN values (which indicate conversion failures)
            if df["work_time"].isna().any():
                msg = "Non-numeric values found in work_time or overtime columns"
                raise ValueError(msg)

            # Then convert to timedelta (numeric values will be treated as hours)
            df["work_time"] = pd.to_timedelta(df["work_time"], unit="h")
            df["overtime"] = pd.to_timedelta(df["overtime"], unit="h")

            weekly_hours = df["work_time"].sum().total_seconds() / self.sec_in_hour
            daily_overtime = df["overtime"].sum().total_seconds() / self.sec_in_hour
            num_days = df[df["work_time"] > pd.Timedelta(0)]["date"].nunique()
            msg = f"Weekly hours: {weekly_hours}, Number of days: {num_days}, Daily overtime: {daily_overtime}"
            logger.debug(msg)
            if num_days == 0:
                logger.warning("No work days found in the log file.")
            else:
                weekly_hours /= num_days  # average work hours per day
                weekly_hours *= 5  # assuming a 5-day work week
                daily_overtime /= num_days

                weekly_result = round(weekly_hours, 2)
                daily_result = round(daily_overtime, 2)
        except (ValueError, TypeError):
            msg = f"{RED}Error converting 'work_time' to timedelta{RESET}"
            logger.exception(msg)
            weekly_result = 0.0
            daily_result = 0.0
        return weekly_result, daily_result

    def get_path(self) -> pathlib.Path:
        """
        Return the path to the logbook file.

        Returns
        -------
        pathlib.Path
            The file path to the logbook CSV file.
        """
        return self.log_path

    def tail(self, n: int = 4) -> None:
        """
        Print the last n lines of the logbook file.

        This method loads the logbook and displays the last n rows
        in a formatted table without row indices.

        Parameters
        ----------
        n : int, default 4
            Number of last rows to display.

        Notes
        -----
        The output is logged using the logger and displayed without
        DataFrame row indices for cleaner formatting.
        """
        df = self.load_logbook().tail(n)

        # sanity check
        if df["work_time"].isna().any() or df["overtime"].isna().any():
            msg = f"{RED}Non-numeric values found in work_time or overtime columns. Please check the logbook file.{RESET}"
            logger.error(msg)
            return

        # change the content of work_time from 9.50 to 9h 30m, and be robust against ""
        df["work_time"] = df["work_time"].apply(lambda x: f"{int(x)}h {int(x % 1 * 60)}m" if x else "")
        df["overtime"] = df["overtime"].apply(lambda x: f"{int(x)}h {int(x % 1 * 60)}m" if x else "")

        title = "\nRecent Entries\n==============="
        msg = title + df.to_string(index=False, header=False)

        logger.info(msg)

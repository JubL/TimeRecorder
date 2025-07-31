"""
Logbook module for managing work time records.

Provides a Logbook class that handles CSV-based time tracking data with features for:
- Loading and saving logbook data
- Adding missing days to the logbook
- Calculating weekly work hours and overtime
- Managing work duration calculations
"""

import logging
import pathlib
from datetime import datetime, timedelta

import colorama
import holidays
import pandas as pd

from src.time_recorder import TimeRecorder

# logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(funcName)s in line %(lineno)s - %(message)s")  # noqa
# logging.basicConfig(level=logging.INFO, format="%(message)s")  # noqa


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
# logger.propagate = False  # Prevent duplicate messages - commented out to allow pytest caplog to work

colorama.init(autoreset=True)
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
RESET = colorama.Style.RESET_ALL

holidays_de_he = holidays.country_holidays("DE", subdiv="HE")


class Logbook:
    """Represents a logbook of work hours.

    This class provides functionality to load, save, and manipulate a logbook of work hours.

    Attributes
    ----------
    log_path : pathlib.Path
        Path to the logbook file.
    """

    def __init__(self, log_path: pathlib.Path, full_format: str = r"%d.%m.%Y %H:%M:%S") -> None:
        """Initialize a Logbook object with the provided parameters.

        Parameters
        ----------
        log_path : pathlib.Path
            Path to the logbook file.
        full_format : str
            Format string for parsing full datetime (default: "%d.%m.%Y %H:%M:%S").
        """
        self.log_path = log_path
        self.full_format = full_format
        self.date_format, self.time_format = self.full_format.split(" ")

        self.sec_in_min = 60  # Number of seconds in a minute
        self.sec_in_hour = 3600  # Number of seconds in an hour
        self.min_in_hour = 60  # Number of minutes in an hour

    def load_logbook(self) -> pd.DataFrame:
        """Load the logbook CSV file into a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            The loaded DataFrame containing the logbook data.

        Notes
        -----
        If the logbook file does not exist or is empty, a new DataFrame is created.
        Handles file not found, empty data, and parsing errors gracefully.
        """
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            self.create_df()  # FIXME remove this functionality?

        try:
            df = pd.read_csv(self.log_path, sep=";", na_values="", encoding="utf-8")  # how are empty fields read? as NaN?
            logger.debug(f"Read logbook from {self.log_path}")
        except FileNotFoundError:
            logger.exception(f"{RED}Log file not found: {self.log_path}{RESET}")
        except pd.errors.EmptyDataError:
            logger.exception(f"{RED}Log file is empty: {self.log_path}{RESET}")
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

    def save_logbook(self, df: pd.DataFrame) -> None:
        """Save a pandas DataFrame to a CSV file.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to be saved.

        Notes
        -----
        The DataFrame is saved using ';' as the separator and UTF-8 encoding.
        Handles OSError and general exceptions gracefully.
        """
        if len(df) > 0 and type(df["date"][0]) is pd.Timestamp:
            # Convert 'date' column to string format if it is in datetime format
            df["date"] = df["date"].dt.strftime(self.date_format)
        try:
            df.to_csv(self.log_path, sep=";", index=False, encoding="utf-8")
            logger.debug(f"Logbook saved to {self.log_path}")
        except PermissionError as e:
            logger.exception(f"{RED}Permission denied when saving logbook to {self.log_path}: {e}{RESET}")
        except OSError as e:
            logger.exception(f"{RED}OS error while saving logbook to {self.log_path}: {e}{RESET}")
        except Exception as e:
            logger.exception(f"{RED}Unexpected error saving logbook to {self.log_path}: {e}{RESET}")

    def record_into_df(self, data: dict) -> None:
        """Write the time report data into a pandas dataframe.

        Parameters
        ----------
        data : dict
            The data to be written to the logbook.
        """
        df = self.load_logbook()
        df.loc[len(df)] = data
        self.save_logbook(df)

    def create_df(self) -> None:
        """Create a pandas dataframe file."""
        columns = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
        df = pd.DataFrame(columns=columns)
        self.save_logbook(df)

    def squash_df(self) -> None:
        """Squash the DataFrame by grouping entries by date and summing work hours.

        This method reads a CSV file, groups the entries by date, and sums the work hours for each date.
        The result is saved back to the same CSV file.

        """

        # FIXME: this is mostly duplicate code from time_recorder.py
        def calculate_total_overtime(row: pd.Series) -> float | str:
            """
            Calculate total overtime for a given row.

            Return empty string if work_time is missing or empty, otherwise calculate overtime.
            """
            if not row["work_time"] or pd.isna(row["work_time"]):
                return ""
            # Overtime is total work_time minus 8 hours (per day)
            overtime = row["work_time"] - 8
            return round(overtime, 2)

        # FIXME: this is mostly duplicate code from time_recorder.py
        def reevaluate_case(row: pd.Series) -> str:
            """Reevaluate the case based on the work_time."""
            if not row["work_time"] or pd.isna(row["work_time"]):
                return ""
            # work_time is in hours (float)
            work_time_td = timedelta(hours=row["work_time"]) if row["work_time"] else timedelta(0)
            case, _ = TimeRecorder.calculate_overtime(work_time_td)
            return case

        df = self.load_logbook()
        df["date"] = pd.to_datetime(df["date"], format=self.date_format)

        # Group by date and weekday, aggregate work_time and lunch_break_duration
        df = (
            df.groupby(["date", "weekday"], as_index=False)
            .agg(
                {
                    "start_time": "first",
                    "end_time": "last",
                    "lunch_break_duration": lambda x: x.sum() if x.notna().any() else "",
                    "work_time": lambda x: x.sum() if x.notna().any() else "",
                },
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
        self.save_logbook(df)
        logger.info(f"{GREEN}Logbook squashed.{RESET}")

    def find_and_add_missing_days(self) -> None:
        """Find and add missing holidays and weekend days to the log file.

        This method checks the log file for missing entries.
        If these days are missing, it adds them with just the weekday and the date.

        Parameters
        ----------
        log_path : pathlib.Path
            The file path to the CSV log file. The file must contain a 'date' column.
        """
        missing_days = self.find_missing_days_in_logbook()

        if missing_days:
            self.add_missing_days_to_logbook(missing_days)

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
                    f"and {df['date'].iloc[i + 1].strftime(self.date_format)}{RESET}",
                )
                missing_days.append((df["date"].iloc[i], df["date"].iloc[i + 1]))

        return missing_days

    def add_missing_days_to_logbook(self, missing_days: list[tuple[datetime, datetime]]) -> None:
        """Add missing Saturdays, Sundays, and holidays to the logbook DataFrame for specified date ranges.

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

        Returns
        -------
        None
        """
        df = self.load_logbook()
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
        df = df.sort_values(by="date", key=lambda x: pd.to_datetime(x, format=self.date_format))
        self.save_logbook(df)

    def get_weekly_hours_from_log(self) -> float:
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

        df = self.load_logbook()

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

    def get_path(self) -> pathlib.Path:
        """Return the path to the logbook file."""
        return self.log_path

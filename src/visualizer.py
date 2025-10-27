"""
TimeRecorder Visualization Module.

This module provides visualization capabilities for work time data using matplotlib.
It includes color schemes for different themes and a Visualizer class for creating
work hours charts.

Color Schemes:
    - ocean: Blue-based theme for professional settings
    - forest: Green-based theme for natural/organic feel
    - sunset: Orange-based theme for warm/energetic mood
    - lavender: Purple-based theme for elegant/creative environments
    - coral: Pink-based theme for modern/friendly aesthetics

Each theme provides separate color palettes for work hours and overtime hours
to ensure clear visual distinction between the two data types.
"""

from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

import src.logging_utils as lu

# Set up logger with centralized configuration
logger = lu.setup_logger(__name__)


COLOR_SCHEMES_WORK = {
    "ocean": ["#1E3A8A", "#1E40AF", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"],
    "forest": ["#14532D", "#166534", "#15803D", "#16A34A", "#22C55E", "#4ADE80"],
    "sunset": ["#9A3412", "#A03E0C", "#C2410C", "#EA580C", "#F97316", "#FB923C"],
    "lavender": ["#581C87", "#5B21B6", "#6B21A8", "#7C3AED", "#A855F7", "#C084FC"],
    "coral": ["#BE185D", "#BE123C", "#DC2626", "#EC4899", "#F472B6", "#F9A8D4"],
}


class Visualizer:
    """
    A class for visualizing work time data with customizable color schemes.

    The Visualizer creates bar charts showing daily work hours and overtime,
    with different colors for each weekday and separate color schemes for
    work hours vs overtime hours.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing work time data with columns:
        - date: Date of the work entry
        - work_time: Regular work hours for the day
        - overtime: Overtime hours for the day
    data : dict
        Configuration dictionary containing:
        - full_format: Date and time format string
        - color_scheme: Theme name for color selection
        - num_months: Number of months to display
        - rolling_average_window_size: Number of days to include in the rolling average
        - standard_work_hours: Standard work hours per day
        - work_days: List of weekday numbers (0=Monday, 6=Sunday)

    Attributes
    ----------
    df : pd.DataFrame
        Processed DataFrame with filtered date range
    work_colors : list
        List of hex color codes for work hours by weekday
    date_format : str
        Date format string extracted from full_format
    time_format : str
        Time format string extracted from full_format
    num_months : int
        Number of months to display in the chart
    rolling_average_window_size : int
        Number of days to include in the rolling average
    standard_work_hours : float
        Standard work hours per day
    work_days : list
        List of weekday numbers to display
    """

    def __init__(self, df: pd.DataFrame, data: dict) -> None:
        """
        Initialize the Visualizer with data and configuration.

        Parameters
        ----------
        df : pd.DataFrame
            Raw work time data DataFrame
        data : dict
            Configuration dictionary with visualization settings
        """
        self.df = df
        self.full_format = data["full_format"]
        self.date_format, self.time_format = self.full_format.split(" ")

        self.work_colors = COLOR_SCHEMES_WORK[data["color_scheme"]]
        self.num_months = data["num_months"]
        self.rolling_average_window_size = data["rolling_average_window_size"]
        self.standard_work_hours = data["standard_work_hours"]
        self.work_days = data["work_days"]

        self.make_logbook_robust()

        # filter the df to only include the last num_months months
        self.df = self.df[self.df["date"] > self.df["date"].max() - pd.DateOffset(months=self.num_months)]

    def make_logbook_robust(self) -> None:
        """
        Make the logbook robust by filling missing values and converting data types.

        This method performs the following data cleaning operations:
        - Converts date column to datetime format
        - Converts work_time and overtime columns to numeric, filling NaN with 0.0
        - Ensures overtime values are non-negative

        Returns
        -------
        None
            Modifies the DataFrame in-place
        """
        self.df["date"] = pd.to_datetime(self.df["date"], format=self.date_format)

        if self.df.empty:
            logger.warning("No data to visualize.")
            return

        self.df.loc[~self.df["start_time"].apply(self.is_valid_time), "work_time"] = -self.standard_work_hours

        # Convert to numeric, coercing errors to NaN, then fill NaN with 0.0
        self.df["work_time"] = pd.to_numeric(self.df["work_time"], errors="coerce").fillna(0.0)
        self.df["overtime"] = pd.to_numeric(self.df["overtime"], errors="coerce").fillna(0.0)

        self.df["overtime"] = self.df["overtime"].where(self.df["overtime"] >= 0.0, 0.0)

    def is_valid_time(self, time_string: str) -> bool:
        """
        Validate whether a time string matches the expected format.

        Parameters
        ----------
        time_string : str
            The time string to validate (e.g., "07:37:15 CEST").

        Returns
        -------
        bool
            True if the time string matches the format, False otherwise.
        """
        if not time_string or pd.isna(time_string):
            return False

        try:
            # First try to parse with timezone
            datetime.strptime(time_string, self.time_format + " %Z")  # noqa: DTZ007
            return True
        except ValueError:
            try:
                # If that fails, try without timezone (strip timezone part)
                time_part = time_string.split(maxsplit=1)[0]  # Get just the time part
                datetime.strptime(time_part, self.time_format)  # noqa: DTZ007
                return True
            except (ValueError, IndexError):
                return False

    def get_rolling_average(self, window: int = 10) -> pd.Series:
        """
        Calculate the rolling average of the work hours.

        Parameters
        ----------
        window : int, default 7
            The number of days to include in the rolling average.

        Returns
        -------
        pd.Series
            The rolling average of the work hours over the last window days.
        """
        if not window:
            return 0.0
        return self.df[self.df["work_time"] > 0]["work_time"].rolling(window=window, min_periods=1).mean()

    def plot_daily_work_hours(self) -> None:
        """
        Create and display a bar chart of daily work hours and overtime.

        This method creates a matplotlib bar chart showing:
        - Work hours for each day as colored bars
        - Overtime hours stacked on top of work hours
        - Different colors for each weekday
        - X-axis showing calendar weeks
        - Y-axis showing work hours

        The chart automatically adjusts work time to exclude overtime
        when total hours exceed standard work hours.

        Returns
        -------
        None
        """
        self.df["rolling_avg"] = self.get_rolling_average(self.rolling_average_window_size)
        self.df["rolling_avg"] = self.df["rolling_avg"].ffill()

        # if work_time is greater than standard_hours, subtract overtime from work_time
        self.df["work_time"] = self.df["work_time"].where(
            self.df["work_time"] <= self.standard_work_hours,
            self.df["work_time"] - self.df["overtime"],
        )

        _, ax = plt.subplots(figsize=(8, 5))

        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.WE))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("KW%U"))
        ax.tick_params(axis="x", which="both", length=0)  # Set x-tick length to 0

        # let each weekday have another color according to the color_scheme
        for i, weekday in enumerate(self.work_days):
            condition_work = (self.df["date"].dt.weekday == weekday) & (self.df["work_time"] > 0)
            condition_free = (self.df["date"].dt.weekday == weekday) & (self.df["work_time"] == -self.standard_work_hours)
            # regular work hours
            ax.bar(
                self.df[condition_work]["date"],
                self.df[condition_work]["work_time"],
                width=1,
                color=self.work_colors[i],
            )
            # overtime hours
            ax.bar(
                self.df[condition_work]["date"],
                self.df[condition_work]["overtime"],
                width=1,
                color=self.work_colors[i + 1],
                bottom=self.df[condition_work]["work_time"],
            )
            # free days (non-weekend days)
            ax.bar(
                self.df[condition_free]["date"],
                abs(self.df[condition_free]["work_time"]),
                width=1,
                color=self.work_colors[-1],
                alpha=0.4,
            )

        ax.plot(self.df["date"], self.df["rolling_avg"], color="black", label="Rolling Average")

        ax.set_xlabel("Calendar Week")
        ax.set_ylabel("Work Hours")
        ax.set_title("Daily Work Hours")

        for i, tick in enumerate(ax.xaxis.get_ticklabels()):
            tick.set_visible(i % 2 == 0)  # Make every other tick visible

        plt.show()

"""
Analyzer module for time tracking data analysis.

This module provides statistical analysis capabilities for time tracking data
stored in logbook DataFrames. The Analyzer class offers various methods to
analyze work patterns, overtime statistics, and identify trends in time tracking data.

Key Features:
- Statistical analysis of overtime patterns
- Mean and standard deviation calculations
- Work pattern analysis
- Data quality checks and validation
"""

import colorama
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

import src.logging_utils as lu

colorama.init(autoreset=True)
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
RESET = colorama.Style.RESET_ALL

logger = lu.setup_logger(__name__)


class Analyzer:
    """
    A comprehensive analyzer for time tracking data.

    The Analyzer class provides statistical analysis and insights into time tracking
    patterns. It processes pandas DataFrames containing work time data and offers
    various analytical methods to understand work patterns, overtime trends, and
    data quality issues.

    Attributes
    ----------
    logbook_df : pd.DataFrame
        The DataFrame containing time tracking data.
        Expected columns include 'date', 'start_time',
        'end_time', 'work_duration', 'overtime', etc.

    Methods
    -------
        mean_and_std(): Calculate mean and standard deviation of overtime
        analyze_work_patterns(): Analyze weekly and monthly work patterns
        detect_outliers(): Identify statistical outliers in work data
        validate_data_quality(): Check for data quality issues
        generate_summary_report(): Generate comprehensive analysis report
    """

    def __init__(self, data: dict, logbook_df: pd.DataFrame) -> None:
        """
        Initialize the Analyzer with a logbook DataFrame.

        Parameters
        ----------
        logbook_df : pd.DataFrame
            DataFrame containing time tracking data.
            Must contain at least an 'overtime' column
            for basic analysis functionality.

        Raises
        ------
        ValueError
            If logbook_df is empty or missing required columns.
        TypeError
            If logbook_df is not a pandas DataFrame.
        """
        if not isinstance(logbook_df, pd.DataFrame):
            raise TypeError("logbook_df must be a pandas DataFrame")

        if logbook_df.empty:
            raise ValueError("logbook_df cannot be empty")

        if "overtime" not in logbook_df.columns:
            logger.warning("DataFrame missing 'overtime' column. Some analysis methods may not work.")

        self.logbook_df = logbook_df.copy()

        self.df = logbook_df.copy()
        self.df["overtime"] = pd.to_numeric(self.df["overtime"], errors="coerce")

        self.standard_work_hours = data["standard_work_hours"]
        self.work_days = data["work_days"]

        self.sec_in_min = 60  # Number of seconds in a minute
        self.sec_in_hour = 3600  # Number of seconds in an hour
        self.min_in_hour = 60  # Number of minutes in an hour

        logger.debug(f"Analyzer initialized with DataFrame containing {len(logbook_df)} rows")

    def mean_and_std(self) -> tuple[float | None, float | None]:
        """
        Calculate and log the mean and standard deviation of overtime.

        This method analyzes the overtime column to provide statistical insights
        into work patterns. It handles missing or invalid data by converting to
        numeric values and ignoring non-numeric entries (coerce mode).

        The results are logged with INFO level and show:
        - Mean overtime in minutes (rounded to nearest minute)
        - Standard deviation of overtime in minutes (rounded to nearest minute)

        If the overtime column contains all NaN values, appropriate warnings
        are logged.

        Returns
        -------
        tuple[float | None, float | None]
            A tuple containing (mean, std) of overtime values in hours.
            Returns (None, None) if no valid overtime data is found.

        Side Effects:
            - Logs statistical results to the configured logger
            - Uses colorama for colored console output if available

        Notes
        -----
            - Overtime values are expected to be in hours (e.g., 0.5 = 30 minutes)
            - Results are converted to minutes for display
            - NaN values are automatically excluded from calculations
        """
        df = self.logbook_df.copy()
        df["overtime"] = pd.to_numeric(df["overtime"], errors="coerce")

        # Check if we have valid data after conversion
        valid_overtime = df["overtime"].dropna()

        if valid_overtime.empty:
            logger.warning(f"{RED}No valid overtime data found for analysis{RESET}")
            return None, None

        return valid_overtime.mean(), valid_overtime.std()

    def analyze_work_patterns(self) -> None:
        """
        Analyze work patterns across different time periods.

        This method provides comprehensive analysis of work patterns including:
        - Weekly work hour averages
        - Monthly trends
        - Day-of-week patterns
        - Seasonal variations (if sufficient data)

        Returns
        -------
        dict[str, Any]
            Dictionary containing analysis results

        Example:
            >>> results = analyzer.analyze_work_patterns()
            >>> print(f"Weekly average: {results['weekly_avg']:.1f} hours")
            Weekly average: 42.3 hours
        """
        # TODO: Implement comprehensive work pattern analysis
        raise NotImplementedError("Work pattern analysis not yet implemented")

    def detect_outliers(self, *, method: str = "iqr", threshold: float = 1.5) -> pd.DataFrame:
        """
        Detect statistical outliers in work data.

        Identifies unusual work patterns that may indicate data entry errors,
        special work days, or other anomalies.

        Parameters
        ----------
        method : str
            Method for outlier detection. Options:
            - 'iqr': Interquartile Range method (default)
            - 'zscore': Z-score method
            - 'isolation_forest': Isolation Forest algorithm
        threshold : float
            Threshold for outlier detection. For IQR method,
            this is the multiplier for the IQR (default: 1.5)

        Returns
        -------
        pd.DataFrame
            DataFrame containing only the outlier entries
        """
        match method:
            case "iqr":
                return self.detect_outliers_iqr(threshold)
            case "zscore":
                return self.detect_outliers_zscore(threshold)
            case "isolation_forest":
                return self.detect_outliers_isolation_forest("auto")
            case _:
                raise ValueError(f"Invalid method: {method}")

    def detect_outliers_iqr(self, threshold: float = 1.5) -> pd.DataFrame:
        """
        Detect outliers using the Interquartile Range (IQR) method.

        Identifies data points that fall outside the IQR range, which is a measure
        of statistical dispersion.

        Parameters
        ----------
        threshold : float
            Multiplier for the IQR to determine outlier threshold

        Returns
        -------
        pd.DataFrame
            DataFrame containing only the outlier entries
        """
        q1 = self.df["overtime"].quantile(0.25)
        q3 = self.df["overtime"].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        return self.df[(self.df["overtime"] < lower_bound) | (self.df["overtime"] > upper_bound)]

    def detect_outliers_zscore(self, threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect outliers using the Z-score method.

        Identifies data points that fall outside a specified number of standard
        deviations from the mean.

        Parameters
        ----------
        threshold : float
            Number of standard deviations from the mean to consider an outlier

        Returns
        -------
        pd.DataFrame
            DataFrame containing only the outlier entries
        """
        mean_overtime = self.df["overtime"].mean()
        std_overtime = self.df["overtime"].std()

        z_scores = (self.df["overtime"] - mean_overtime) / std_overtime
        return self.df[abs(z_scores) > threshold]

    def detect_outliers_isolation_forest(self, threshold: float | str = "auto") -> pd.DataFrame:
        """
        Detect outliers using the Isolation Forest algorithm.

        Identifies data points that are significantly different from the majority
        of the data.

        Parameters
        ----------
        threshold : float
            Threshold for anomaly score to consider an outlier

        Returns
        -------
        pd.DataFrame
            DataFrame containing only the outlier entries
        """
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(self.df[["overtime"]])

        model = IsolationForest(contamination=threshold)
        self.df["anomaly_score"] = model.fit_predict(df_scaled)

        return self.df[self.df["anomaly_score"] == -1]

    def validate_data_quality(self) -> None:
        """
        Validate the quality and consistency of time tracking data.

        Performs various data quality checks including:
        - Missing values detection
        - Data type validation
        - Logical consistency checks (e.g., end_time > start_time)
        - Duplicate entry detection
        - Date range validation

        Returns
        -------
        dict[str, Any]
            Dictionary containing validation results with keys:
            - 'missing_values': Count of missing values by column
            - 'data_type_issues': List of data type inconsistencies
            - 'logical_errors': List of logical inconsistencies
            - 'duplicates': Number of duplicate entries
            - 'overall_score': Overall data quality score (0-100)
        """
        # TODO: Implement data quality validation
        raise NotImplementedError("Data quality validation not yet implemented")

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

        df = self.logbook_df.copy()

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
                weekly_hours *= len(self.work_days)
                daily_overtime /= num_days

                weekly_result = round(weekly_hours, 2)
                daily_result = round(daily_overtime, 2)
        except (ValueError, TypeError):
            msg = f"{RED}Error converting 'work_time' to timedelta{RESET}"
            logger.exception(msg)
            weekly_result = 0.0
            daily_result = 0.0
        return weekly_result, daily_result

    def generate_summary_report(self) -> None:
        """
        Generate a comprehensive summary report of all analyses.

        Creates a formatted report containing all available analysis results
        in a human-readable format.

        Returns
        -------
        str
            Formatted summary report as a string
        """
        mean, std = self.mean_and_std()
        weekly_hours, daily_overtime = self.get_weekly_hours_from_log()
        weekly_standard_hours = self.standard_work_hours * len(self.work_days)

        outliers = self.detect_outliers()

        # Handle case where mean_and_std returns None values
        if mean is not None and std is not None:
            mean_str = f"Mean overtime per work day: {int(mean)}h {mean % 1 * 60:.0f}m"
            std_str = f"Standard Deviation of overtime: {int(std)}h {std % 1 * 60:.0f}m"
        else:
            mean_str = "Mean overtime per work day: No valid data available"
            std_str = "Standard Deviation of overtime: No valid data available"
        avr_weekly_hours = f"Average Weekly Hours: {int(weekly_hours)}h {int(weekly_hours % 1 * 60)}m"
        standard_hours_str = f"Standard Hours: {int(weekly_standard_hours)}h"
        if weekly_standard_hours % 1 != 0:
            standard_hours_str += f" {int(weekly_standard_hours % 1 * 60)}m"
        daily_overtime_str = f"Mean Daily Overtime: {int(daily_overtime)}h {int(daily_overtime % 1 * 60)}m"
        outliers_str = f"Outliers: {outliers}"

        title = "\nAnalytics\n========="

        # Combine all parts
        items = [title, mean_str, std_str, avr_weekly_hours, standard_hours_str, daily_overtime_str, "", outliers_str]
        logger.info("\n".join(items))

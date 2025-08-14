"""
Argument parser module for the time_recorder project.

Provides an ArgumentParser class that handles command line argument parsing
and validation for the time recorder application.
"""

import argparse
import pathlib

import src.logging_utils as lu

# Set up logger with centralized configuration
logger = lu.setup_logger(__name__)


class TimeRecorderArgumentParser:
    """Argument parser for the time recorder application.

    This class handles parsing and validation of command line arguments
    for the time recorder application, ensuring proper argument combinations
    and providing clear error messages.

    Attributes
    ----------
    parser : argparse.ArgumentParser
        The underlying argparse parser instance.
    """

    def __init__(self) -> None:
        """Initialize the argument parser with all required arguments."""
        self.parser = argparse.ArgumentParser(
            description="""
Time recorder
A powerful and flexible Python tool for tracking and managing work hours.""",
            formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=105, max_help_position=45),
        )
        self._setup_arguments()

    def _setup_arguments(self) -> None:
        """Set up all command line arguments."""
        # Time specification arguments (intentionally not mutually exclusive)
        self.parser.add_argument("--boot", action=argparse.BooleanOptionalAction, help="Use system boot time.")
        self.parser.add_argument("--date", type=str, help="Date in DD.MM.YYYY format")
        self.parser.add_argument("--start", type=str, help="Start time in HH:MM:SS format")

        # Time completion arguments
        self.parser.add_argument("--end", type=str, help="End time in HH:MM:SS format")
        self.parser.add_argument("--end_now", action="store_true", help="End time is one minute from now.")
        self.parser.add_argument("--lunch", type=int, help="Lunch break duration in minutes")

        # Processing control arguments
        self.parser.add_argument("--log", action="store_true", help="Log the results.")
        self.parser.add_argument("--squash", action=argparse.BooleanOptionalAction, help="Squash the logbook.")
        self.parser.add_argument(
            "--add_missing",
            action=argparse.BooleanOptionalAction,
            help="Add missing days to the logbook.",
        )
        self.parser.add_argument("--weekly", action=argparse.BooleanOptionalAction, help="Calculate weekly hours.")
        self.parser.add_argument("--tail", type=int, help="Show the last n lines of the logbook.")

        # Configuration arguments
        self.parser.add_argument("--config", type=str, help="Path to the config file", default="config.yaml")
        self.parser.add_argument("--logbook", type=str, help="Path to the logbook file")

        # Visualization arguments
        self.parser.add_argument("--plot", action="store_true", help="Create visualizations from logbook data")
        self.parser.add_argument("--num_months", type=int, help="Number of months to show in daily hours plot")
        self.parser.add_argument(
            "--color_scheme",
            type=str,
            choices=["ocean", "forest", "sunset", "lavender", "coral"],
            help="Color scheme for visualizations",
        )

        # Version argument
        self.parser.add_argument("--version", action="version", version=f"Version: {self.get_project_version()}")

    def parse_args(self) -> argparse.Namespace:
        """
        Parse command line arguments and validate them.

        Returns
        -------
        argparse.Namespace
            Parsed command line arguments.
        """
        args = self.parser.parse_args()
        self.validate_time_arguments(args)
        return args

    @staticmethod
    def validate_time_arguments(args: argparse.Namespace) -> None:
        """
        Validate that the time arguments follow the required logic.

        Parameters
        ----------
        args : argparse.Namespace
            Parsed command line arguments.
        """
        # Check if any time specification method is provided
        has_boot = args.boot
        has_date = isinstance(args.date, str) and args.date is not None
        has_start = isinstance(args.start, str) and args.start is not None

        has_end = isinstance(args.end, str) and args.end is not None
        has_end_now = args.end_now

        # Case 1: --boot is selected (no --date or --start should be provided)
        if has_boot:
            if has_date or has_start:
                logger.warning(
                    "The usage of --boot together with --date or --start does not make much sense."
                    "Use either --boot OR both --date and --start together.",
                )

        # Case 2: Manual time specification (both --date and --start must be provided)
        elif (has_date or has_start) and not (has_date and has_start):
            logger.warning(
                "When not using --boot, both --date and --start must be provided. Use either --boot OR both --date and --start together.",
            )

        # Case 3: Both end and end_now were specified
        if has_end and has_end_now:
            logger.warning("The usage of --end and --end_now together does not make much sense. Use either --end OR --end_now.")

    def get_help_text(self) -> str:
        """
        Get the help text for the argument parser.

        Returns
        -------
        str
            Formatted help text for the argument parser.
        """
        return self.parser.format_help()

    def print_help(self) -> None:
        """Print the help text to stdout."""
        self.parser.print_help()

    def print_usage(self) -> None:
        """Print the usage text to stdout."""
        self.parser.print_usage()

    @staticmethod
    def get_project_version() -> str:
        """
        Get the project version from the pyproject.toml file.

        Returns
        -------
        str
            The project version.
        """
        version = "unknown"
        try:
            with pathlib.Path("pyproject.toml").open(encoding="utf-8") as file:
                for line in file:
                    if "version" in line:
                        version = line.split("=")[1].strip().strip('"')
                        break
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError):
            pass
        return version


def run_arg_parser() -> argparse.Namespace:
    """
    Run the argument parser conveniently.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments.
    """
    parser = TimeRecorderArgumentParser()
    return parser.parse_args()

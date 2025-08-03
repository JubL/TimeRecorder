#!/usr/bin/env python3
"""
Argument parser module for the time_recorder project.

Provides an ArgumentParser class that handles command line argument parsing
and validation for the time recorder application.
"""

import argparse


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
        self.parser = argparse.ArgumentParser(description="Time recorder")
        self._setup_arguments()

    def _setup_arguments(self) -> None:
        """Set up all command line arguments."""
        # Time specification arguments (intentionally not mutually exclusive)
        self.parser.add_argument("--boot", action="store_true", help="Use system boot time")
        self.parser.add_argument("--date", type=str, help="Date (DD.MM.YYYY)")
        self.parser.add_argument("--start", type=str, help="Start time (HH:MM:SS)")

        # Time completion arguments
        self.parser.add_argument("--end", type=str, help="End time (HH:MM:SS)")
        self.parser.add_argument("--lunch", type=int, help="Lunch break duration in minutes")

        # Processing control arguments
        self.parser.add_argument("--log", action="store_true", help="Log the results")
        self.parser.add_argument("--no_squash", action="store_false", help="Do not squash the logbook")
        self.parser.add_argument("--no_missing", action="store_false", help="Do not add missing days to the logbook")
        self.parser.add_argument("--no_weekly", action="store_false", help="Do not calculate weekly hours")
        self.parser.add_argument("--no_tail", action="store_false", help="Do not show the last n lines of the logbook")

        # Configuration arguments
        self.parser.add_argument("--config", type=str, help="Path to the config file", default="config.yaml")
        self.parser.add_argument("--logbook", type=str, help="Path to the logbook file", default="timereport_logbook.txt")

    def parse_args(self) -> argparse.Namespace:
        """
        Parse command line arguments and validate them.

        Returns
        -------
        argparse.Namespace
            Parsed command line arguments.

        Raises
        ------
        SystemExit
            If argument validation fails.
        """
        args = self.parser.parse_args()
        self._validate_time_arguments(args)
        return args

    def _validate_time_arguments(self, args: argparse.Namespace) -> None:
        """
        Validate that the time arguments follow the required logic.

        Parameters
        ----------
        args : argparse.Namespace
            Parsed command line arguments.

        Raises
        ------
        SystemExit
            If validation fails with appropriate error message.
        """
        # Check if any time specification method is provided
        has_boot = args.boot
        has_date = args.date is not None
        has_start = args.start is not None

        # Case 1: --boot is selected (no --date or --start should be provided)
        if has_boot:
            if has_date or has_start:
                raise SystemExit(
                    "Error: --boot cannot be used together with --date or --start. "
                    "Use either --boot OR both --date and --start together.",
                )

        # Case 2: Manual time specification (both --date and --start must be provided)
        elif has_date or has_start:
            if not (has_date and has_start):
                raise SystemExit(
                    "Error: When not using --boot, both --date and --start must be provided. "
                    "Use either --boot OR both --date and --start together.",
                )

        # Case 3: No time specification method provided
        else:
            raise SystemExit(
                "Error: You must specify either --boot OR both --date and --start. No time specification method was provided.",
            )

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


def run_arg_parser() -> argparse.Namespace:
    """
    Run the argument parser conveniently.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments.

    Raises
    ------
    SystemExit
        If argument validation fails.
    """
    parser = TimeRecorderArgumentParser()
    return parser.parse_args()

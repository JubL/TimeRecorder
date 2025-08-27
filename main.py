"""
Main module for the time_recorder project.

Provides a main function that creates a TimeRecorder object and a Logbook object,
and uses them to record the time and log the results.
"""

import pathlib

import src.arg_parser as ap
import src.config_utils as cu
import src.logging_utils as lu
from src.logbook import Logbook
from src.time_recorder import TimeRecorder
from src.visualizer import Visualizer


def main() -> None:
    """Run the main function of the time recorder."""
    # TODO: increase the test coverage to 95%

    # TODO: visualization of work hours per day, week, month, year
    # TODO: calc overtime mean and std dev
    # TODO: introduce outlier detection, consistency checks?

    # TODO: shall tail() be controlled by the --log flag? maybe put it in a analyse category together with features yet to come?

    # TODO: add this weeks or last weeks average work hours and compare with the historic weekly work hours

    # TODO: shall full_format (from the config.yaml) include a field for the timezone? (e.g. %Z) Test this (with a different timezone).

    # TODO: add color scheme black or gray

    args = ap.run_arg_parser()

    # Create default config if it doesn't exist
    config_path = pathlib.Path(args.config or "config.yaml")
    if not config_path.exists():
        cu.create_default_config(config_path)

    config: dict[str, dict] = cu.load_config(config_path)

    # Set global log level first (change this to control all logging)
    # Options: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
    lu.set_global_log_level(config["logging"]["log_level"])

    # Set up main logger
    logger = lu.setup_logger(__name__)

    if not cu.validate_config(config):
        logger.error("Configuration validation failed")
        raise SystemExit(1)

    # Update the config with the command line arguments
    config = cu.update_config(config, args)

    # Extract configuration sections
    time_recorder_config = cu.get_time_recorder_config(config)
    logbook_config = cu.get_logbook_config(config)
    processing_config = cu.get_processing_config(config)
    display_config = cu.get_display_config(config)
    visualization_config = cu.get_visualization_config(config)
    logger.debug("Configuration loaded successfully")

    # Create TimeRecorder object from configuration
    tr_line = TimeRecorder(data=time_recorder_config)
    logbook = Logbook(data=logbook_config)

    # Process based on configuration
    if processing_config["use_boot_time"]:
        tr_line.update_boot_time()

    tr_line.print_state()

    if processing_config["log_enabled"]:
        tr_dict = tr_line.time_report_line_to_dict()
        logbook.record_into_df(tr_dict)

        if processing_config["add_missing_days"]:
            logbook.find_and_add_missing_days()

        if processing_config["auto_squash"]:
            logbook.squash_df()

    if processing_config["calculate_weekly_hours"]:
        logbook.print_weekly_summary()

    if processing_config["log_enabled"]:
        logbook.tail(display_config["show_tail"])

    if visualization_config["plot"]:
        visualizer = Visualizer(logbook.load_logbook(), visualization_config)
        visualizer.plot_daily_work_hours()


if __name__ == "__main__":
    main()

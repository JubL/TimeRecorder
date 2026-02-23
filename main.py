"""
Main module for the time_recorder project.

Provides a main function that creates a TimeRecorder object and a Logbook object,
and uses them to record the time and log the results.
"""

import pathlib

import src.arg_parser as ap
import src.config_utils as cu
import src.logging_utils as lu
from src.analyzer import Analyzer
from src.logbook import Logbook
from src.time_recorder import TimeRecorder
from src.visualizer import Visualizer


def main() -> None:
    """Run the main function of the time recorder."""
    # TODO: Visualize work hours per day, week, month, year in one plot with four graphs.
    # TODO: Give the user a notice if there is too little data to show the graphs.
    # TODO: Show histogramm of work start time and work end time.
    # TODO: Show histogramm of lunch break duration and overtime.

    # TODO: Implement outlier detection, consistency checks?

    # TODO: Shall tail() be controlled by the --log flag? Maybe put it in a analyse category together with features yet to come?

    # TODO: Shall full_format (from the config.yaml) include a field for the timezone? (e.g. %Z) Test this (with a different timezone).

    # TODO: Implement report generation in PDF, XLSX, and HTML format.

    # TODO: Write floats into the log with exactly two decimal places.

    # TODO: Is squashing the log a bad idea?
    # TODO: Maybe don't squash the logbook, but only the pandas dataframe for the presentation and visualization of the data?

    # TODO: Execution take surprisingly long. Find out where the time is lost. Use a profiler to find the bottlenecks.
    # TODO: Load the logbook only once!

    # TODO: Have an overtime feature that tracks the overtime and let's you take off days from the overtime to compensate for it.

    # TODO: Build an UI for the time recorder with Figma Make?

    # TODO: The tests should take the default config and then modify the values that need to be different. (done for test_visualizer)
    # TODO: check that test use fixtures (done for test_visualizer)

    args = ap.run_arg_parser()

    # Create default config if it doesn't exist
    config_path = pathlib.Path(args.config or "config.yaml")
    if not config_path.exists():
        cu.create_default_config(config_path)
    config: dict[str, dict] = cu.load_config(config_path)

    if not cu.validate_config(config):
        msg = f"Configuration validation failed. Please check the {config_path!s} file."
        raise SystemExit(msg)

    # Update the config with the command line arguments
    config = cu.update_config(config, args)

    # Set global log level first (change this to control all logging)
    # Options: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
    lu.set_global_log_level(config["logging"]["log_level"])
    # Set up main logger
    logger = lu.setup_logger(__name__)

    # Extract configuration sections
    time_recorder_config = cu.get_time_recorder_config(config)
    logbook_config = cu.get_logbook_config(config)
    processing_config = cu.get_processing_config(config)
    display_config = cu.get_display_config(config)
    visualization_config = cu.get_visualization_config(config)
    analyzer_config = cu.get_analyzer_config(config)
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

        logbook.tail(display_config["show_tail"])

    if analyzer_config["analyze_work_patterns"]:
        analyzer = Analyzer(data=analyzer_config, logbook_df=logbook.load_logbook())
        analyzer.generate_summary_report()

    if visualization_config["plot"]:
        visualizer = Visualizer(logbook.load_logbook(), visualization_config)
        visualizer.create_histogram()
        visualizer.create_daily_work_hours_plot()
        visualizer.display_all_plots()


if __name__ == "__main__":
    main()

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
    # TODO: Implement outlier detection, consistency checks?
    # TODO: test for correct format in logbook
    # TODO: test for a consequitive sequence of days (no missing days)

    # TODO: Shall full_format (from the config.yaml) include a field for the timezone? (e.g. %Z) Test this (with a different timezone).

    # TODO: Build an UI for the time recorder with Figma Make?

    # TODO: Make the work_schedule.work_days from config.yaml a set instead of a list?

    # TODO: Providing the flags --no-boot, --date, and --start altogether is overly complicated if one only wants
    # TODO: to set either the date or the start. It would be better to only provide what is needed.
    # TODO: This is because update_boot_time() is executed much later in the program's flow than update_config().
    # TODO: If the boot time were read out and set in the config before update_config() was executed, the order of
    # TODO: execution and thus the necessary CLI flags would make much more sense. However, the update_boot_time()
    # TODO: method would need to be moved from the TimeRecorder class.

    args = ap.run_arg_parser()

    # Create default config if it doesn't exist, then load it
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
    lu.set_global_log_level(config["logging"]["log_level"])
    # Set up main logger
    logger = lu.setup_logger(__name__)

    # Extract configuration sections
    time_recorder_config = cu.get_time_recorder_config(config)
    logbook_config = cu.get_logbook_config(config)
    processing_config = cu.get_processing_config(config)
    visualization_config = cu.get_visualization_config(config)
    analyzer_config = cu.get_analyzer_config(config)
    logger.debug("Configuration loaded successfully")

    # Create TimeRecorder from configuration
    tr_line = TimeRecorder(data=time_recorder_config)

    # Create Logbook from configuration
    log_enabled = processing_config["log_enabled"]
    analyze_work_patterns = analyzer_config["analyze_work_patterns"]
    plot_enabled = visualization_config["plot"]
    logbook: Logbook | None = None
    if log_enabled or analyze_work_patterns or plot_enabled:
        logbook = Logbook(data=logbook_config)
    if logbook is None:
        msg = "Since no processing or visualisation has been configured, no logbook will be created."
        logger.debug(msg)

    # Process based on configuration
    if processing_config["use_boot_time"]:
        tr_line.update_boot_time()

    tr_line.print_state()

    if log_enabled:
        assert logbook is not None
        tr_dict = tr_line.time_report_line_to_dict()
        logbook.record_into_df(tr_dict)
        if processing_config["add_missing_days"]:
            logbook.find_and_add_missing_days()
        if processing_config["auto_squash"]:
            logbook.squash_df_keep_originals()

    if analyze_work_patterns:
        assert logbook is not None
        analyzer = Analyzer(data=analyzer_config, logbook_df=logbook.get_logbook())
        analyzer.generate_summary_report()
        analyzer.tail(analyzer_config["show_tail"])

    if plot_enabled:
        assert logbook is not None
        visualizer = Visualizer(logbook.get_logbook(), visualization_config)
        visualizer.display_all_plots()


if __name__ == "__main__":
    main()

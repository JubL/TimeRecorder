# TimeRecorder Configuration

This document explains how to use the YAML configuration system for the TimeRecorder project.

## Overview

The TimeRecorder project supports YAML-based configuration, allowing you to customize various aspects of the application without modifying the source code. The configuration is stored in a `config.yaml` file that is automatically created with default values when the application runs for the first time (if that file is missing).

## Configuration file structure

The `config.yaml` file is organized into these sections (all are **required** for validation to succeed):

### Data processing settings

```yaml
data_processing:
  use_boot_time: true     # Use system boot time as start time
  logging_enabled: false  # Append the computed line to the logbook when true
  auto_squash: true       # After logging: aggregate duplicate date/weekday rows (see below)
  add_missing_days: true  # Fill gaps with weekends/holidays where applicable
```

When `auto_squash` is true and a log line is written, the logbook runs aggregation that merges multiple rows for the same calendar day. Original rows are kept as commented lines (weekday prefixed with `#--`), and one summarized row is written after them.

### Time tracking settings

```yaml
time_tracking:
  date: "01.08.2025"                # Date in DD.MM.YYYY format
  start_time: "07:00"               # Start time in HH:MM format
  end_time: "17:25"                 # End time in HH:MM format
  lunch_break_duration: 60          # Duration of the lunch break in minutes
  full_format: "%d.%m.%Y %H:%M:%S"  # Format string used for parsing/combining date and time fields
```

Optional keys such as `end_now` may be merged in from the CLI when used; they are not required in the file.

### Logging settings

```yaml
logging:
  log_path: "timereport_logbook.csv"  # Path to the log file (supports multiple formats)
  log_level: "INFO"                   # Logging level: DEBUG, INFO, WARNING, ERROR
```

**Note**: The `log_path` supports multiple file formats. Simply change the file extension to use a different format:

| Extension | Format |
|-----------|--------|
| `.csv`, `.txt`, `.dat` | CSV (semicolon-separated; project default) |
| `.json` | JSON |
| `.xlsx`, `.xls` | Excel |
| `.html` | HTML |
| `.parquet`, `.pq` | Parquet |
| `.xml` | XML |
| `.yaml`, `.yml` | YAML |

### Work schedule settings

```yaml
work_schedule:
  standard_work_hours: 8      # Expected hours per work day (used for overtime/undertime)
  work_days: [0, 1, 2, 3, 4]  # Monday to Friday (0=Monday, 6=Sunday)
  timezone: "Europe/Berlin"   # IANA timezone name for time calculations
```

### Holiday settings

```yaml
holidays:
  country: "DE"      # Country code for the `holidays` library
  subdivision: "HE"  # Region/state (e.g. Hesse)
```

### Visualization settings

```yaml
visualization:
  plot: false                      # Whether to open plots when plot mode runs
  color_scheme: "ocean"            # ocean | forest | sunset | lavender | coral
  num_months: 13                   # Months of history for daily-hours style plots
  rolling_average_window_size: 10  # Days in rolling-average overlays
  x_tick_interval: 4               # Spacing for x-axis ticks (weeks, depending on plot)
  histogram_bin_width: 10          # Histogram bin width in minutes
```

### Analyzer settings

```yaml
analyzer:
  analyze_work_patterns: false  # Run statistical summary and tail when true
  outlier_method: "iqr"         # iqr | zscore | isolation_forest
  outlier_threshold: 1.5        # Method-specific threshold
  show_tail: 5                  # Lines to show from the log tail in the report
```

## Usage

### Automatic configuration creation

When you run TimeRecorder and `config.yaml` is missing, a default file is created next to the working directory (see `create_default_config` in `src/config_utils.py`). Defaults may differ slightly from a hand-tuned repo `config.yaml`; compare with your project’s checked-in file if you track one.

### Manual configuration

1. Place `config.yaml` where you run the app (or pass `--config`).
2. Match the required sections and keys listed above so `validate_config` passes.
3. Run the application.

### Command line arguments

Overrides are merged after loading YAML (`update_config` in `src/config_utils.py`). Only arguments you pass replace values; omitted flags leave the file as-is.

#### Time specification

```bash
# Use system boot time
python main.py --boot     # use_boot_time: true (default behavior)
python main.py --no-boot  # use_boot_time: false

# Specify custom date and start time
python main.py --date "25.07.2025" --start "08:30"

# Set end time
python main.py --end "17:30"
python main.py --end_now  # end time = one minute from now (merged into config)

# Set lunch break duration
python main.py --lunch 45
```

#### Processing and logging

```bash
# Enable logging to logbook
python main.py --log             # logging_enabled: true

# Control data processing
python main.py --squash          # auto_squash: true

python main.py --add-missing     # add_missing_days: true

# Show last n lines of logbook
python main.py --tail 10         # analyzer.show_tail
```

#### Configuration paths

```bash
# Use custom configuration file
python main.py --config my_config.yaml

# Use custom logbook file
python main.py --logbook my_logbook.csv   # sets logging.log_path (relative name is resolved from cwd)
```

#### Visualization

```bash
# Show work hours visualization
python main.py --show-plot

python main.py --color-scheme forest
python main.py --num-months 6
python main.py --rolling-average-window-size 14
```

#### Analyzer

```bash
python main.py --analyze

python main.py --outlier-method zscore
python main.py --outlier-threshold 3.0
```

#### Information

```bash
# Show version
python main.py --version

# Show help
python main.py --help
```

### Argument validation

The parser warns when combinations are confusing (for example `--boot` together with `--date` / `--start`, incomplete `--date`/`--start` pairs, or both `--end` and `--end_now`).

### Configuration validation

Startup validation (`validate_config`) fails if:

- Any required **section** is missing: `data_processing`, `time_tracking`, `logging`, `work_schedule`, `holidays`, `visualization`, `analyzer`.
- Any required **field** in those sections is missing (including `visualization.rolling_average_window_size`, `visualization.x_tick_interval`, and all `analyzer` keys listed above).
- The YAML cannot be parsed.

## Example configuration

```yaml
# TimeRecorder configuration

data_processing:
  use_boot_time: false             # Don't use boot time
  logging_enabled: true            # Enable logging
  auto_squash: true                # Automatically squash duplicate entries
  add_missing_days: true           # Add missing days to logbook

time_tracking:
  date: "30.12.2024"               # Custom date
  start_time: "08:30"              # Later start time
  end_time: "18:00"                # Later end time
  lunch_break_duration: 45         # Shorter lunch break
  full_format: "%d.%m.%Y %H:%M:%S"

logging:
  log_path: "my_work_log.csv"      # Custom log file name
  log_level: "DEBUG"               # More verbose logging

work_schedule:
  standard_work_hours: 3.75        # Part-time work schedule
  work_days: [0, 1, 2, 3]          # Monday to Thursday only
  timezone: "America/New_York"     # Different timezone

holidays:
  country: "US"                    # US holidays
  subdivision: "NY"                # New York state

visualization:
  plot: true                       # Enable visualization by default
  color_scheme: "forest"           # Use forest color scheme
  num_months: 6                    # Show last 6 months

analyzer:
  analyze_work_patterns: true      # Enable work pattern analysis
```

## Configuration functions (`src/config_utils.py`)

- `load_config(config_path)`: Load YAML.
- `validate_config(config)`: Check required sections and fields.
- `create_default_config(config_path)`: Write a default file if missing.
- `update_config(config, args)`: Apply CLI overrides.
- `get_time_recorder_config(config)`: Parameters for `TimeRecorder`.
- `get_logbook_config(config)`: Parameters for `Logbook` (including absolute `log_path`).
- `get_processing_config(config)`: `use_boot_time`, `log_enabled`, `auto_squash`, `add_missing_days`.
- `get_visualization_config(config)`: Plot styling, rolling average, ticks, histogram, plus schedule/format passthrough.
- `get_analyzer_config(config)`: Analysis flags, outlier settings, tail, rolling window from visualization.

## Feature notes

### Boot time

With `use_boot_time: true`, the recorder can take the system boot time as the start of the work interval (see `TimeRecorder`).

### Logbook path

Paths under `logging.log_path` are combined with the **current working directory** when building `Logbook` (`get_logbook_config`).

### Missing days

`add_missing_days` uses gap detection and inserts placeholder rows for weekends and configured holidays.

### Multi-format logbooks

Handlers are chosen by file extension (`src/formats/registry.py`). Excel may require `openpyxl`; XML may require `lxml`, depending on your environment.

### Work pattern analysis

When `analyzer.analyze_work_patterns` is true (or overridden with `--analyze`), the analyzer runs summaries including weekly hour estimates and optional outlier detection, controlled by `outlier_method` and `outlier_threshold`.

### Visualization

Plots use `visualization.*` options; color schemes are fixed sets defined in the visualizer.

## Troubleshooting

1. **Missing config**: A default is created only when the file is absent; otherwise edit or remove/rename to regenerate.
2. **Invalid YAML**: Use a YAML linter or validator.
3. **Validation errors**: Compare your file to the required keys in `validate_config` in `src/config_utils.py`.
4. **Permissions**: Ensure write access for the logbook path.
5. **Optional dependencies**: Some formats need extra packages (`openpyxl`, `lxml`, etc.).

### Logging levels

Set `logging.log_level` to `DEBUG`, `INFO`, `WARNING`, or `ERROR` (see `src/logging_utils.py`).

## Advanced examples

```bash
# Record with boot time and write to logbook
python main.py --boot --log

# Fixed interval
python main.py --date "25.07.2025" --start "08:00" --end "17:00" --log

# Turn off squash/missing-day steps for this run
python main.py --boot --log --no-squash --no-add_missing

python main.py --tail 20

python main.py --plot --color-scheme sunset --num-months 3

python main.py --config custom_config.yaml --logbook custom_log.csv
```

Have fun logging!

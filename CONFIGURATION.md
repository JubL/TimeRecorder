# TimeRecorder Configuration

This document explains how to use the YAML configuration system for the TimeRecorder project.

## Overview

The TimeRecorder project supports YAML-based configuration, allowing you to customize various aspects of the application without modifying the source code. The configuration is stored in a `config.yaml` file that is automatically created with default values when the application runs for the first time.

## Configuration File Structure

The `config.yaml` file is organized into several sections:

### Data Processing Settings

```yaml
data_processing:
  use_boot_time: true          # Use system boot time as start time
  logging_enabled: false        # Set to True to log the results
  auto_squash: true            # Automatically squash duplicate entries
  add_missing_days: true       # Add missing days to logbook
```

### Time Tracking Settings

```yaml
time_tracking:
  date: "01.08.2025"          # Date in DD.MM.YYYY format
  start_time: "07:00"          # Starting time in HH:MM format
  end_time: "17:25"            # Ending time in HH:MM format
  lunch_break_duration: 60     # Duration of the lunch break in minutes
  full_format: "%d.%m.%Y %H:%M:%S"  # Format string for parsing full datetime
```

### Logging Settings

```yaml
logging:
  log_path: "timereport_logbook.txt"  # Path to the log file (relative to current directory)
  log_level: "INFO"            # Logging level: DEBUG, INFO, WARNING, ERROR
```

### Work Schedule Settings

```yaml
work_schedule:
  standard_work_hours: 8       # Standard work hours per day
  work_days: [0, 1, 2, 3, 4]  # Monday to Friday (0=Monday, 6=Sunday)
  timezone: "Europe/Berlin"    # Timezone for time calculations
```

### Holiday Settings

```yaml
holidays:
  country: "DE"                # Country code for holidays
  subdivision: "HE"            # State/province subdivision
```

### Display Settings

```yaml
display:
  calculate_weekly_hours: true # Calculate weekly hours from log
  calculate_daily_overhours: true  # Calculate daily overhours from log
  show_tail: 4                 # Show the last n lines of the logbook
```

## Usage

### Automatic Configuration Creation

When you run the TimeRecorder application for the first time, it will automatically create a `config.yaml` file with default values in the current directory.

### Manual Configuration

You can manually create or modify the `config.yaml` file to customize the application behavior:

1. Create a `config.yaml` file in the same directory as your `main.py`
2. Copy the structure above and modify the values as needed
3. Run the application - it will use your custom configuration

### Command Line Arguments

TimeRecorder supports various command line arguments to override configuration settings:

#### Time Specification Arguments
```bash
# Use system boot time (default behavior)
python main.py --boot

# Specify custom date and start time
python main.py --date "25.07.2025" --start "08:30"

# Set end time
python main.py --end "17:30"

# Set end time to one minute from now
python main.py --end_now

# Set lunch break duration
python main.py --lunch 45
```

#### Processing Control Arguments
```bash
# Enable logging to logbook
python main.py --log

# Control data processing (default: enabled)
python main.py --squash          # Enable/disable squashing
python main.py --add_missing     # Enable/disable adding missing days
python main.py --weekly          # Enable/disable weekly calculations

# Show last n lines of logbook
python main.py --tail 10
```

#### Configuration Arguments
```bash
# Use custom configuration file
python main.py --config my_config.yaml

# Use custom logbook file
python main.py --logbook my_logbook.txt
```

#### Information Arguments
```bash
# Show version
python main.py --version

# Show help
python main.py --help
```

### Argument Validation

The application validates command line arguments and provides warnings for potentially conflicting combinations:

- Using `--boot` together with `--date` or `--start` (though allowed, does not make sense)
- Using both `--end` and `--end_now` together
- Providing only one of `--date` or `--start` when not using `--boot`

### Configuration Validation

The application validates the configuration file on startup and will display an error if:
- Required sections are missing (`time_tracking`, `logging`, `work_schedule`)
- Required fields within sections are missing
- The YAML file is malformed

## Example Configuration

Here's a complete example of a custom configuration:

```yaml
# TimeRecorder Configuration File
# This file contains all configurable parameters for the TimeRecorder application

# Data processing settings
data_processing:
  use_boot_time: false             # Don't use boot time
  logging_enabled: true            # Enable logging
  auto_squash: true                # Automatically squash duplicate entries
  add_missing_days: true           # Add missing days to logbook

# Time tracking settings
time_tracking:
  date: "30.12.2024"               # Custom date
  start_time: "08:30"              # Later start time
  end_time: "18:00"                # Later end time
  lunch_break_duration: 45         # Shorter lunch break
  full_format: "%d.%m.%Y %H:%M:%S"

# Logging settings
logging:
  log_path: "my_work_log.txt"      # Custom log file name
  log_level: "DEBUG"               # More verbose logging

# Work schedule settings
work_schedule:
  standard_work_hours: 3.75        # Part-time work schedule
  work_days: [0, 1, 2, 3]          # Monday to Thursday only
  timezone: "America/New_York"     # Different timezone

# Holiday settings
holidays:
  country: "US"                    # US holidays
  subdivision: "NY"                # New York state

# Display settings
display:
  calculate_weekly_hours: true     # Calculate weekly hours from log
  calculate_daily_overhours: true  # Calculate daily overhours from log
  show_tail: 10                    # Show more recent entries
```

## Configuration Functions

The configuration system provides several utility functions in `src/config_utils.py`:

- `load_config(config_path: pathlib.Path) -> dict`: Load configuration from YAML file
- `validate_config(config: dict) -> bool`: Validate configuration structure
- `get_time_recorder_config(config: dict) -> dict`: Extract TimeRecorder parameters
- `get_logbook_config(config: dict) -> dict`: Extract Logbook parameters
- `get_display_config(config: dict) -> dict`: Extract display parameters
- `get_processing_config(config: dict) -> dict`: Extract processing parameters
- `create_default_config(config_path: pathlib.Path) -> None`: Create default configuration file
- `update_config(config: dict, args: argparse.Namespace) -> dict`: Update configuration with command line arguments

## Key Features

### System Boot Time Integration

TimeRecorder can automatically detect your work start time from system boot time:

```yaml
data_processing:
  use_boot_time: true  # Automatically use system boot time as start time
```

### End Time Options

You can specify end time in multiple ways:

```bash
# Use specific end time
python main.py --end "17:30"

# Use current time (one minute from now)
python main.py --end_now

# Use end time from configuration file
python main.py
```

**Note**: The `--end_now` argument sets the end time to one minute from the current time. This feature is supported via command line and will be added to the configuration when used.

### Missing Day Detection

Automatically add missing work days to your logbook:

```yaml
data_processing:
  add_missing_days: true  # Add missing days with default values
```

### Data Aggregation

Automatically squash duplicate entries and aggregate data:

```yaml
data_processing:
  auto_squash: true  # Remove duplicates and aggregate by date
```

### Weekly Hours Calculation

Calculate and display weekly work hour summaries:

```yaml
display:
  calculate_weekly_hours: true  # Calculate weekly hours from log
```

### Flexible Time Specification

You can specify work times in multiple ways:

1. **Boot time mode**: `--boot` (uses system boot time as start)
2. **Manual mode**: `--date "DD.MM.YYYY" --start "HH:MM"`
3. **Configuration mode**: Use values from `config.yaml`



## Troubleshooting

### Common Issues

1. **Configuration file not found**: The application will create a default `config.yaml` file automatically
2. **Invalid YAML syntax**: Check the YAML syntax using an online validator
3. **Missing required fields**: The application will show which fields are missing
4. **Permission errors**: Ensure you have write permissions in the directory

### Validation Errors

The application validates the configuration and will show specific error messages for:
- Missing required sections (`time_tracking`, `logging`, `work_schedule`)
- Missing required fields within sections
- Invalid data types or values

### Logging

The application uses structured logging with different levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program execution
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for problems that need attention

You can control the logging level in the configuration:

```yaml
logging:
  log_level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
```

### Command Line Argument Conflicts

The application provides warnings for potentially conflicting argument combinations:

```bash
# This will show a warning
python main.py --boot --date "25.07.2025" --start "08:00"

# This will show a warning
python main.py --end "17:30" --end_now
```

## Advanced Usage Examples

### Basic Time Recording
```bash
# Record today's work with boot time
python main.py --boot --log

# Record specific work hours
python main.py --date "25.07.2025" --start "08:00" --end "17:00" --log

# Record work ending now
python main.py --date "25.07.2025" --start "08:00" --end_now --log
```

### Data Processing
```bash
# Disable automatic data processing
python main.py --boot --log --no_squash --no_missing

# Show more logbook entries
python main.py --tail 20

# Disable weekly calculations
python main.py --boot --log --no_weekly
```

### Custom Configuration
```bash
# Use custom config file
python main.py --config custom_config.yaml

# Use custom logbook file
python main.py --config custom_config.yaml --logbook custom_log.txt
```

Have fun logging!
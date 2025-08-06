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

### Command Line Overrides

You can override configuration settings via command line arguments:

```bash
# Use system boot time and enable logging
python main.py --boot --log

# Override specific time settings
python main.py --start-time "08:30" --end-time "17:30" --lunch-break 45

# Use custom configuration file
python main.py --config my_config.yaml
```

### Configuration Validation

The application validates the configuration file on startup and will display an error if:
- Required sections are missing
- Required fields within sections are missing
- The YAML file is malformed

## Example Configuration

Here's a complete example of a custom configuration:

```yaml
# TimeRecorder Configuration File
# This file contains all configurable parameters for the TimeRecorder application

# Data processing settings
data_processing:
  use_boot_time: false         # Don't use boot time
  logging_enabled: true         # Enable logging
  auto_squash: true            # Automatically squash duplicate entries
  add_missing_days: true       # Add missing days to logbook

# Time tracking settings
time_tracking:
  date: "30.12.2024"          # Custom date
  start_time: "08:30"          # Later start time
  end_time: "18:00"            # Later end time
  lunch_break_duration: 45     # Shorter lunch break
  full_format: "%d.%m.%Y %H:%M:%S"

# Logging settings
logging:
  log_path: "my_work_log.txt"  # Custom log file name
  log_level: "DEBUG"           # More verbose logging

# Work schedule settings
work_schedule:
  standard_work_hours: 7.5     # Part-time work schedule
  work_days: [0, 1, 2, 3]     # Monday to Thursday only
  timezone: "America/New_York" # Different timezone

# Holiday settings
holidays:
  country: "US"                # US holidays
  subdivision: "NY"            # New York state

# Display settings
display:
  calculate_weekly_hours: true # Calculate weekly hours from log
  calculate_daily_overhours: true  # Calculate daily overhours from log
  show_tail: 10               # Show more recent entries
```

## Configuration Functions

The configuration system provides several utility functions:

- `load_config()`: Load configuration from YAML file
- `validate_config()`: Validate configuration structure
- `get_time_recorder_config()`: Extract TimeRecorder parameters
- `get_logbook_config()`: Extract Logbook parameters
- `get_display_config()`: Extract display parameters
- `get_processing_config()`: Extract processing parameters
- `create_default_config()`: Create default configuration file

## Key Features

### System Boot Time Integration

TimeRecorder can automatically detect your work start time from system boot time:

```yaml
data_processing:
  use_boot_time: true  # Automatically use system boot time as start time
```

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

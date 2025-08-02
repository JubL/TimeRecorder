# TimeRecorder Configuration

This document explains how to use the YAML configuration system for the TimeRecorder project.

## Overview

The TimeRecorder project now supports YAML-based configuration, allowing you to customize various aspects of the application without modifying the source code. The configuration is stored in a `config.yaml` file that is automatically created with default values when the application runs for the first time.

## Configuration File Structure

The `config.yaml` file is organized into several sections:

### Time Tracking Settings

```yaml
time_tracking:
  use_boot_time: true          # Use system boot time as start time
  date: "25.07.2025"          # Date in DD.MM.YYYY format
  start_time: "07:00"          # Starting time in HH:MM format
  end_time: "17:25"            # Ending time in HH:MM format
  lunch_break_duration: 60     # Duration of the lunch break in minutes
  full_format: "%d.%m.%Y %H:%M:%S"  # Format string for parsing full datetime
```

### Logging Settings

```yaml
logging:
  enabled: false               # Set to True to log the results
  log_path: "timereport_logbook.txt"  # Path to the log file
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
  include_holidays: true       # Whether to include holidays in calculations
```

### Data Processing Settings

```yaml
data_processing:
  auto_squash: true            # Automatically squash duplicate entries
  add_missing_days: true       # Add missing days to logbook
  calculate_weekly_hours: true # Calculate weekly hours from log
```

### Output Settings

```yaml
output:
  colored_output: true         # Use colored terminal output
  show_statistics: true        # Show overtime/undertime statistics
  export_format: "csv"         # Export format: csv, json, excel
```

## Usage

### Automatic Configuration Creation

When you run the TimeRecorder application for the first time, it will automatically create a `config.yaml` file with default values in the current directory.

### Manual Configuration

You can manually create or modify the `config.yaml` file to customize the application behavior:

1. Create a `config.yaml` file in the same directory as your `main.py`
2. Copy the structure above and modify the values as needed
3. Run the application - it will use your custom configuration

### Configuration Validation

The application validates the configuration file on startup and will display an error if:
- Required sections are missing
- Required fields within sections are missing
- The YAML file is malformed

## Example Configuration

Here's a complete example of a custom configuration:

```yaml
# TimeRecorder Configuration File
time_tracking:
  use_boot_time: false         # Don't use boot time
  date: "30.12.2024"          # Custom date
  start_time: "08:30"          # Later start time
  end_time: "18:00"            # Later end time
  lunch_break_duration: 45     # Shorter lunch break
  full_format: "%d.%m.%Y %H:%M:%S"

logging:
  enabled: true                # Enable logging
  log_path: "my_work_log.txt"  # Custom log file name
  log_level: "DEBUG"           # More verbose logging

work_schedule:
  standard_work_hours: 7.5     # Part-time work schedule
  work_days: [0, 1, 2, 3]     # Monday to Thursday only
  timezone: "America/New_York" # Different timezone

holidays:
  country: "US"                # US holidays
  subdivision: "NY"            # New York state
  include_holidays: true

data_processing:
  auto_squash: false           # Don't auto-squash
  add_missing_days: true
  calculate_weekly_hours: true

output:
  colored_output: false        # No colored output
  show_statistics: true
  export_format: "json"        # Export as JSON
```

## Configuration Functions

The configuration system provides several utility functions:

- `load_config()`: Load configuration from YAML file
- `validate_config()`: Validate configuration structure
- `get_time_recorder_config()`: Extract TimeRecorder parameters
- `get_logbook_config()`: Extract Logbook parameters
- `get_processing_config()`: Extract processing parameters
- `create_default_config()`: Create default configuration file

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

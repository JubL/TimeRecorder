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
  log_path: "timereport_logbook.csv"  # Path to the log file (supports multiple formats)
  log_level: "INFO"            # Logging level: DEBUG, INFO, WARNING, ERROR
```

**Note**: The `log_path` supports multiple file formats. Simply change the file extension to use a different format:

- `timereport_logbook.csv` - CSV format (default)
- `timereport_logbook.json` - JSON format
- `timereport_logbook.yaml` - YAML format
- `timereport_logbook.xlsx` - Excel format
- `timereport_logbook.xml` - XML format
- `timereport_logbook.parquet` - Parquet format

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

### Visualization Settings

```yaml
visualization:
  show_plot: false             # Show work hours visualization
  color_scheme: "ocean"        # Color scheme: ocean, forest, sunset, lavender, coral
  num_months: 12               # Number of months to display in visualization
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
python main.py --logbook my_logbook.csv
```

#### Visualization Arguments
```bash
# Show work hours visualization
python main.py --show-plot

# Use specific color scheme
python main.py --show-plot --color-scheme forest

# Show visualization for specific number of months
python main.py --show-plot --num-months 6

# Combine visualization with other options
python main.py --show-plot --color-scheme sunset --num-months 3
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
  log_path: "my_work_log.csv"      # Custom log file name
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

# Visualization settings
visualization:
  show_plot: true                  # Enable visualization by default
  color_scheme: "forest"           # Use forest color scheme
  num_months: 6                    # Show last 6 months
```

## Configuration Functions

The configuration system provides several utility functions in `src/config_utils.py`:

- `load_config(config_path: pathlib.Path) -> dict`: Load configuration from YAML file
- `validate_config(config: dict) -> bool`: Validate configuration structure
- `get_time_recorder_config(config: dict) -> dict`: Extract TimeRecorder parameters
- `get_logbook_config(config: dict) -> dict`: Extract Logbook parameters
- `get_display_config(config: dict) -> dict`: Extract display parameters
- `get_processing_config(config: dict) -> dict`: Extract processing parameters
- `get_visualization_config(config: dict) -> dict`: Extract visualization parameters
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

### Multi-Format File Support

TimeRecorder supports multiple file formats for storing your time records. The system automatically detects the format based on the file extension and uses the appropriate handler.

#### Supported Formats

- **CSV** (`.csv`, `.txt`) - Comma-separated values with UTF-8 encoding
- **JSON** (`.json`) - JavaScript Object Notation for easy data exchange
- **YAML** (`.yaml`, `.yml`) - Human-readable configuration format
- **Excel** (`.xlsx`, `.xls`) - Microsoft Excel spreadsheet format
- **XML** (`.xml`) - Extensible Markup Language for enterprise integration
- **Parquet** (`.parquet`, `.pq`) - Columnar storage format for large datasets

#### Format Selection

To use a different format, simply change the file extension in your configuration:

```yaml
logging:
  log_path: "timereport_logbook.xlsx"  # Excel format
  log_path: "timereport_logbook.json"  # JSON format
```

#### Format Interoperability

All formats maintain the same data structure and are fully interoperable. You can:
- Convert between formats by changing the file extension
- Use different formats for different use cases
- Share data across different systems and applications

#### Format-Specific Features

- **CSV**: Simple, widely supported format
- **JSON**: Easy data exchange and API integration
- **YAML**: Human-readable configuration format
- **Excel**: Business-friendly with formatting capabilities
- **XML**: Enterprise integration and structured data
- **Parquet**: Efficient storage for large datasets

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

### Data Visualization

TimeRecorder includes a powerful visualization feature that creates beautiful bar charts showing your daily work hours and overtime. The visualization helps you identify patterns in your work schedule and track overtime trends.

#### Available Color Schemes

The visualizer supports five beautiful color schemes:

- **Ocean**: Deep blue tones (#1E3A8A to #60A5FA)
- **Forest**: Rich green tones (#14532D to #22C55E)
- **Sunset**: Warm orange tones (#9A3412 to #F97316)
- **Lavender**: Elegant purple tones (#581C87 to #A855F7)
- **Coral**: Vibrant pink tones (#BE185D to #F472B6)

#### Visualization Features

- **Separate Work and Overtime**: Work hours and overtime are displayed as separate bars with distinct colors
- **Color-Coded by Weekday**: Each weekday has its own color within the selected scheme
- **Automatic Data Filtering**: Shows only the specified number of months
- **Responsive Design**: Charts automatically adjust to your data



## Troubleshooting

### Common Issues

1. **Configuration file not found**: The application will create a default `config.yaml` file automatically
2. **Invalid YAML syntax**: Check the YAML syntax using an online validator
3. **Missing required fields**: The application will show which fields are missing
4. **Permission errors**: Ensure you have write permissions in the directory
5. **Format-specific errors**: Some formats require additional dependencies:
   - Excel format requires `openpyxl` package
   - XML format requires `lxml` package
   - These are automatically installed with the main package

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
python main.py --config custom_config.yaml --logbook custom_log.csv
```

### Multi-Format Examples
```bash
# Use Excel format for business reporting
python main.py --config excel_config.yaml --logbook work_hours.xlsx

# Use JSON format for API integration
python main.py --config json_config.yaml --logbook time_data.json

# Use XML format for enterprise systems
python main.py --config xml_config.yaml --logbook time_data.xml
```

### Visualization Examples
```bash
# Show visualization with default settings
python main.py --show-plot

# Use a specific color scheme
python main.py --show-plot --color-scheme forest

# Show last 6 months of data
python main.py --show-plot --num-months 6

# Combine visualization with time recording
python main.py --boot --log --show-plot --color-scheme sunset

# Show visualization for specific time period
python main.py --show-plot --color-scheme coral --num-months 3
```

Have fun logging!
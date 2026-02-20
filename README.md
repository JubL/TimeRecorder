# TimeRecorder ⏰

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Mypy](https://img.shields.io/badge/Mypy-passing-brightgreen.svg)](https://mypy-lang.org/)
[![Test Status](https://github.com/python/mypy/actions/workflows/test.yml/badge.svg)](https://github.com/JubL/TimeRecorder/actions)
[![Test Coverage](https://img.shields.io/badge/Test%20Coverage-99%25-brightgreen.svg)](https://github.com/JubL/TimeRecorder)

A powerful and flexible Python tool for tracking and managing work hours with automatic overtime calculations, system boot time integration, and comprehensive reporting features.

## ✨ Features

- **🕐 Time Tracking**: Record work hours with start/end times and lunch breaks
- **⚡ System Boot Integration**: Automatically detect work start time from system boot
- **📊 Overtime Calculations**: Calculate overtime/undertime based on standard eight-hour work days (configurable)
- **📈 Weekly Reports**: Generate weekly work hour summaries with detailed analysis
- **🎨 Colored Output**: Visual feedback with color-coded overtime (green) and undertime (red)
- **📝 Multi-Format Logbook**: Persistent storage of all time records in multiple file formats
- **🔧 Flexible Configuration**: YAML-based configuration system for easy customization
- **🌍 Holiday Support**: Automatic holiday detection
- **📱 Missing Day Detection**: Automatically add missing days (weekends, holidays) to your logbook
- **🔄 Data Processing**: Automatic duplicate removal and data aggregation
- **📋 Recent Entries Display**: View the last n entries from your logbook with formatted time display
- **📊 Advanced Data Visualization**: Generate bar charts showing daily work hours and overtime with rolling average trends, plus a histogram of work hours distribution
- **📈 Rolling Average Analysis**: Track work time trends with configurable rolling average window
- **🧪 Comprehensive Testing**: Extensive test suite with high coverage across all modules

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/JubL/TimeRecorder.git
   cd TimeRecorder
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Run TimeRecorder**:
   ```bash
   python main.py
   ```

The application will automatically create a `config.yaml` file with default settings on the first run.

### Basic Usage

```bash
# Record today's work hours with default settings
python main.py

# Use the system boot time as the start time
# and also log the work hours in the logbook
python main.py --boot --log

# Use custom configuration file
python main.py --config my_config.yaml

# Override specific settings via command line
python main.py --date "25.07.2025" --start "08:30" --end "17:30" --lunch 45

# Note: When --date and --start are provided together, --no-boot is automatically set
# You don't need to explicitly use --no-boot in this case

# Show visualization with custom color scheme
python main.py --plot --color-scheme ocean
python main.py --plot --color-scheme forest
python main.py --plot --color-scheme sunset
python main.py --plot --color-scheme lavender
python main.py --plot --color-scheme coral

# Show visualization for last 6 months
python main.py --plot --num-months 6

```

## 📋 Configuration

TimeRecorder uses a YAML configuration file (`config.yaml`) for all settings. Here's a complete example:

```yaml
# Time tracking settings
time_tracking:
  use_boot_time: true               # Use system boot time as start time
  date: "25.07.2025"                # Date in DD.MM.YYYY format
  start_time: "07:00"               # Starting time in HH:MM format
  end_time: "17:25"                 # Ending time in HH:MM format
  lunch_break_duration: 60          # Duration of the lunch break in minutes
  full_format: "%d.%m.%Y %H:%M:%S"  # Format string for parsing full datetime

# Logging settings
logging:
  enabled: false                      # Set to True to log the results
  log_path: "timereport_logbook.csv"  # Path to the log file (supports multiple formats)
  log_level: "INFO"                   # Logging level: DEBUG, INFO, WARNING, ERROR

# Work schedule settings
work_schedule:
  standard_work_hours: 8      # Standard work hours per day
  work_days: [0, 1, 2, 3, 4]  # Monday to Friday (0=Monday, 6=Sunday)
  timezone: "Europe/Berlin"   # Timezone for time calculations

# Holiday settings
holidays:
  country: "DE"           # Country code for holidays
  subdivision: "HE"       # State/province subdivision

# Data processing settings
data_processing:
  auto_squash: true             # Automatically squash duplicate entries
  add_missing_days: true        # Add missing days to logbook
  calculate_weekly_hours: true  # Calculate weekly hours from log

# Output settings
output:
  colored_output: true   # Use colored terminal output
  show_statistics: true  # Show overtime/undertime statistics
  export_format: "csv"   # Export format: csv, json, excel
  show_tail: 5           # Show the last n lines of the logbook

# Visualization settings
visualization:
  plot: false            # Show work hours visualization
  color_scheme: "ocean"  # Color scheme: ocean, forest, sunset, lavender, coral
  num_months: 13         # Number of months to display in visualization
  rolling_average_window_size: 10  # Number of days for rolling average calculation
  x_tick_interval: 4     # Number of weeks between x-axis ticks
  histogram_bins: 64     # Number of bins for the work hours histogram
```

For detailed configuration documentation, see [CONFIGURATION.md](CONFIGURATION.md).

## 📊 Example Output

```
TimeRecorder - Work Hours Calculator
====================================
📅 Date: Mon, 25.07.2025
⏰ Start Time: 07:00 CEST
⏰ End Time: 17:25 CEST
🍽️ Lunch Break: 60 m
⏱️ Work Duration: 9h 25m (9.42h)
📈 Status: overtime 1h 25m (1.42h)

Weekly Summary:
==============
Average Weekly Hours: 42h 15m
Standard Hours: 40h 0m
Mean Daily Overtime: +2h 15m

Recent Entries:
===============
Mon 25.07.2025 07:00:12 CEST 17:25:00 CEST 9h 25m overtime 1h 25m
Fri 22.07.2025 08:00:53 CEST 17:00:00 CEST 8h 0m overtime 0h 0m
Thu 21.07.2025 07:45:38 CEST 16:30:00 CEST 7h 45m undertime -0h 15m
```

## 🧪 Testing

TimeRecorder includes a comprehensive test suite with high coverage across all modules. The test suite is designed to ensure reliability and maintainability of the codebase.

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "fast"           # Fast unit tests
pytest -m "integration"    # Integration tests
pytest -m "slow"          # Slow tests

# Run specific test modules
pytest tests/test_logbook/
pytest tests/test_time_recorder/

# Run specific test files
pytest tests/test_logbook/test_tail.py
pytest tests/test_logbook/test_load_logbook.py

# Run tests with verbose output
pytest -v

# Run tests and show local variables on failures
pytest -l
```

## 📊 Data Visualization

TimeRecorder includes a powerful visualization feature that creates two complementary plots when enabled:

1. **Daily Work Hours Chart**: A bar chart showing your daily work hours and overtime with a rolling average trend line
2. **Work Hours Histogram**: A histogram showing the distribution of total work hours per day across your work days

Both plots are displayed simultaneously in separate windows. The visualization helps you identify patterns in your work schedule, track overtime trends, and analyze long-term work patterns.

### Available Color Schemes

The visualizer supports five beautiful color schemes:

- **Ocean**: Deep blue tones (#1E3A8A to #60A5FA)
- **Forest**: Rich green tones (#14532D to #22C55E)
- **Sunset**: Warm orange tones (#9A3412 to #F97316)
- **Lavender**: Elegant purple tones (#581C87 to #A855F7)
- **Coral**: Vibrant pink tones (#BE185D to #F472B6)

### Using Visualization

```bash
# Show visualization with default settings
python main.py --plot

# Use a specific color scheme
python main.py --plot --color-scheme forest

# Show last 6 months of data
python main.py --plot --num-months 6

# Combine with other options
python main.py --plot --color-scheme sunset --num-months 3

# Try different color schemes
python main.py --plot --color-scheme lavender
python main.py --plot --color-scheme coral
```

### Visualization Features

- **Dual Plot Display**: Daily work hours chart and work hours histogram shown simultaneously in separate windows
- **Work Hours Histogram**: Distribution of total work hours per day (days with work > 0 only), with configurable bin count
- **Separate Work and Overtime**: Work hours and overtime are displayed as separate bars with distinct colors
- **Rolling Average Trend Line**: Black trend line shows the rolling average of work hours over a configurable window
- **Color-Coded by Weekday**: Each weekday has its own color within the selected scheme
- **Automatic Data Filtering**: Shows only the specified number of months
- **Responsive Design**: Charts automatically adjust to your data
- **Robust Data Handling**: Automatically handles missing data, invalid time formats, and data type conversions
- **Time Validation**: Validates time strings and handles timezone information gracefully
- **Calendar Week Display**: X-axis shows calendar weeks for easy reference
- **Configurable Rolling Window**: Adjust the rolling average window size
- **Customizable X-Axis Tick Interval**: Control the spacing of x-axis ticks (e.g., every 4 weeks)
- **Configurable Histogram Bins**: Adjust the number of bins in the work hours histogram (default: 64)

### Configuration

You can configure visualization settings in your `config.yaml`:

```yaml
visualization:
  plot: true                   # Enable visualization by default
  color_scheme: "ocean"        # Choose your preferred color scheme
  num_months: 13               # Number of months to display
  rolling_average_window_size: 10  # Days to include in rolling average (default: 10)
  x_tick_interval: 4           # Number of weeks between x-axis ticks (default: 4)
  histogram_bins: 64           # Number of bins for work hours histogram (default: 64)
```

### Rolling Average Configuration

The rolling average feature helps you identify trends in your work patterns by calculating the average work hours over a sliding window of days. This is particularly useful for:

- **Trend Analysis**: See if your work hours are increasing or decreasing over time
- **Pattern Recognition**: Identify seasonal patterns or workload changes
- **Goal Tracking**: Monitor progress toward work-life balance goals
- **Anomaly Detection**: Spot unusual work patterns that might need attention

**Configuration Options:**
- **Small Window (5-7 days)**: Shows short-term trends and weekly patterns
- **Medium Window (10-14 days)**: Balances responsiveness with stability (recommended default)
- **Large Window (20-30 days)**: Shows long-term trends and smooths out daily variations

## 🔧 Advanced Features

### System Boot Time Integration

TimeRecorder can automatically detect your work start time from system boot time:

```yaml
time_tracking:
  use_boot_time: true  # Automatically use system boot time as start time
```

**Note:** When you provide both `--date` and `--start` arguments together, the system automatically disables boot time usage. You don't need to explicitly use `--no-boot` in this case.

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

### Recent Entries Display

View the last n entries from your logbook with formatted time display:

```yaml
output:
  show_tail: 5  # Show the last 5 entries (default)
```

The `tail()` method displays work time in a human-readable format (e.g., "7h 30m" instead of "7.5").

### File Format Support

TimeRecorder supports multiple file formats for storing your time records. Simply specify the desired format in your configuration by changing the file extension:

```yaml
logging:
  log_path: "timereport_logbook.csv"   # CSV format
  log_path: "timereport_logbook.json"  # JSON format
  log_path: "timereport_logbook.xlsx"  # Excel format
  log_path: "timereport_logbook.pq"    # Parquet format
  log_path: "timereport_logbook.xml"   # XML format
  log_path: "timereport_logbook.yaml"  # YAML format
```

#### Supported Formats

- **CSV** (`.csv`, `.txt`, `.dat`) - Comma-separated values with UTF-8 encoding
- **JSON** (`.json`) - JavaScript Object Notation for easy data exchange
- **YAML** (`.yaml`, `.yml`) - Human-readable configuration format with column preservation
- **Excel** (`.xlsx`, `.xls`) - Microsoft Excel spreadsheet format
- **XML** (`.xml`) - Extensible Markup Language for enterprise integration
- **Parquet** (`.parquet`, `.pq`) - Columnar storage format for large datasets

The system automatically detects the format based on the file extension and uses the appropriate handler. All formats maintain the same data structure and are fully interoperable.

#### Format-Specific Features

Each format handler includes comprehensive features:

- **CSV Handler**: UTF-8 encoding, automatic column detection, robust error handling
- **JSON Handler**: Records wrapper format, nested structure support, unicode handling
- **YAML Handler**: Column order preservation, YAML-specific features (anchors, comments), block style output
- **Excel Handler**: Multiple sheet support, data type preservation, openpyxl integration
- **XML Handler**: Custom XML structure, attribute support, enterprise integration
- **Parquet Handler**: Columnar storage, compression support, large dataset optimization

#### Extensible Format System

TimeRecorder uses a **Strategy Pattern** for file format handling, making it easy to add new formats. The system includes:

- **Automatic Format Detection**: Based on file extension
- **Unified Interface**: All formats implement the same `BaseFormatHandler` interface
- **Easy Extension**: Adding new formats requires minimal code changes
- **Format Registry**: Centralized mapping of file extensions to handlers
- **Comprehensive Testing**: Each format handler includes 30+ tests for reliability

For developers interested in adding new formats, see the [formats module documentation](src/formats/README.md).

## 🛠️ Development

### Project Structure

```
TimeRecorder/
├── main.py                 # Main application entry point
├── config.yaml             # Configuration file (auto-generated)
├── CONFIGURATION.md        # Detailed configuration documentation
├── pyproject.toml          # Project configuration and dependencies
├── src/                    # Source code
│   ├── __init__.py         # Package initialization
│   ├── arg_parser.py       # Command line argument parsing
│   ├── config_utils.py     # Configuration utilities
│   ├── formats/            # File format handlers
│   │   ├── __init__.py     # Format registry and handlers
│   │   ├── base.py         # Base format handler interface
│   │   ├── csv_handler.py  # CSV format handler
│   │   ├── json_handler.py # JSON format handler
│   │   ├── yaml_handler.py # YAML format handler
│   │   ├── excel_handler.py # Excel format handler
│   │   ├── xml_handler.py  # XML format handler
│   │   └── parquet_handler.py # Parquet format handler
│   ├── logbook.py          # Logbook management
│   ├── logging_utils.py    # Logging configuration
│   ├── time_recorder.py    # Core time tracking functionality
│   └── visualizer.py       # Data visualization functionality
└── tests/                  # Comprehensive test suite
    ├── conftest.py         # Pytest configuration and shared fixtures
    ├── test_formats/       # File format handler tests (200+ tests)
    ├── test_config_utils/  # Configuration utility tests
    ├── test_logbook/       # Logbook management tests
    ├── test_logging_utils/ # Logging utility tests
    ├── test_time_recorder/ # Core functionality tests
    ├── test_visualizer/    # Visualization functionality tests
    └── test_arg_parser/    # Argument parsing tests
```

### Code Quality

The project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check code quality
ruff check .

# Format code
ruff format .

# Fix auto-fixable issues
ruff check --fix .
```

### Development Workflow

1. **Write Tests First**: All new features should include comprehensive tests
2. **Maintain Coverage**: Aim for high test coverage across all modules
3. **Follow Patterns**: Use established patterns for format handlers and testing
4. **Document Changes**: Update documentation for any new features or changes

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write comprehensive tests for your changes
4. Ensure all tests pass and maintain high coverage
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Testing Requirements

- All new code must include comprehensive tests
- Maintain or improve test coverage

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ using Python 3.13+
- Uses [pandas](https://pandas.pydata.org/) for data manipulation
- [matplotlib](https://matplotlib.org/) for data visualization
- [colorama](https://github.com/tartley/colorama) for colored terminal output
- [holidays](https://github.com/dr-prodigy/python-holidays) for holiday detection
- [psutil](https://github.com/giampaolo/psutil) for system information
- [openpyxl](https://openpyxl.readthedocs.io/) for Excel file support
- [lxml](https://lxml.de/) for XML file support
- [PyYAML](https://pyyaml.org/) for YAML file support
- [pyarrow](https://arrow.apache.org/docs/python/) for Parquet file support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JubL/TimeRecorder/issues)
- **Documentation**: [CONFIGURATION.md](CONFIGURATION.md)
- **Email**: jubin@lirawi.de

---

**Made with ⏰ by [Jubin Lirawi](https://github.com/JubL)**
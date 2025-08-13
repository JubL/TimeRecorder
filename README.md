# TimeRecorder ⏰

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Test Status](https://github.com/python/mypy/actions/workflows/test.yml/badge.svg)](https://github.com/JubL/TimeRecorder/actions)
[![Build Status](https://travis-ci.com/yourname/yourproject.svg?branch=master)](https://travis-ci.com/JubL/TimeRecorder)
[![Test Coverage](https://img.shields.io/badge/test%20coverage-82%25-brightgreen.svg)](https://github.com/JubL/TimeRecorder)

A powerful and flexible Python tool for tracking and managing work hours with automatic overtime calculations, system boot time integration, and comprehensive reporting features.

## ✨ Features

- **🕐 Time Tracking**: Record work hours with start/end times and lunch breaks
- **⚡ System Boot Integration**: Automatically detect work start time from system boot
- **📊 Overtime Calculations**: Calculate overtime/undertime based on standard eight-hour work days (configurable)
- **📈 Weekly Reports**: Generate weekly work hour summaries with detailed analysis
- **🎨 Colored Output**: Visual feedback with color-coded overtime (green) and undertime (red)
- **📝 CSV Logbook**: Persistent storage of all time records in CSV format
- **🔧 Flexible Configuration**: YAML-based configuration system for easy customization
- **🌍 Holiday Support**: Automatic holiday detection
- **📱 Missing Day Detection**: Automatically add missing work days (weekends, holidays) to your logbook
- **🔄 Data Processing**: Automatic duplicate removal and data aggregation
- **📋 Recent Entries Display**: View the last n entries from your logbook with formatted time display

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
python main.py --start-time "08:30" --end-time "17:30" --lunch-break 45
```

## 📋 Configuration

TimeRecorder uses a YAML configuration file (`config.yaml`) for all settings. Here's a complete example:

```yaml
# Time tracking settings
time_tracking:
  use_boot_time: true          # Use system boot time as start time
  date: "25.07.2025"          # Date in DD.MM.YYYY format
  start_time: "07:00"          # Starting time in HH:MM format
  end_time: "17:25"            # Ending time in HH:MM format
  lunch_break_duration: 60     # Duration of the lunch break in minutes
  full_format: "%d.%m.%Y %H:%M:%S"  # Format string for parsing full datetime

# Logging settings
logging:
  enabled: false               # Set to True to log the results
  log_path: "timereport_logbook.txt"  # Path to the log file
  log_level: "INFO"            # Logging level: DEBUG, INFO, WARNING, ERROR

# Work schedule settings
work_schedule:
  standard_work_hours: 8       # Standard work hours per day
  work_days: [0, 1, 2, 3, 4]  # Monday to Friday (0=Monday, 6=Sunday)
  timezone: "Europe/Berlin"    # Timezone for time calculations

# Holiday settings
holidays:
  country: "DE"                # Country code for holidays
  subdivision: "HE"            # State/province subdivision
  include_holidays: true       # Whether to include holidays in calculations

# Data processing settings
data_processing:
  auto_squash: true            # Automatically squash duplicate entries
  add_missing_days: true       # Add missing days to logbook
  calculate_weekly_hours: true # Calculate weekly hours from log

# Output settings
output:
  colored_output: true         # Use colored terminal output
  show_statistics: true        # Show overtime/undertime statistics
  export_format: "csv"         # Export format: csv, json, excel
  show_tail: 4                 # Show the last n lines of the logbook
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

## 🔧 Advanced Features

### System Boot Time Integration

TimeRecorder can automatically detect your work start time from system boot time:

```yaml
time_tracking:
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

### Recent Entries Display

View the last n entries from your logbook with formatted time display:

```yaml
output:
  show_tail: 4  # Show the last 4 entries (default)
```

The `tail()` method displays work time in a human-readable format (e.g., "7h 30m" instead of "7.5").

### Export Options

Export your time records in various formats:

```yaml
output:
  export_format: "csv"  # Options: csv, json, excel
```

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
│   ├── logbook.py          # Logbook management
│   ├── logging_utils.py    # Logging configuration
│   └── time_recorder.py    # Core time tracking functionality
└── tests/                  # Test suite
    ├── conftest.py         # Pytest configuration
    ├── test_config_utils/  # Configuration utility tests
    ├── test_logbook/       # Logbook management tests
    ├── test_logging_utils/ # Logging utility tests
    └── test_time_recorder/ # Core functionality tests
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

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ using Python 3.12+
- Uses [pandas](https://pandas.pydata.org/) for data manipulation
- [colorama](https://github.com/tartley/colorama) for colored terminal output
- [holidays](https://github.com/dr-prodigy/python-holidays) for holiday detection
- [psutil](https://github.com/giampaolo/psutil) for system information

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JubL/TimeRecorder/issues)
- **Documentation**: [CONFIGURATION.md](CONFIGURATION.md)
- **Email**: jubin@lirawi.de

---

**Made with ⏰ by [Jubin Lirawi](https://github.com/JubL)**
# TimeRecorder ⏰

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/JubL/TimeRecorder)
[![Test Coverage](https://img.shields.io/badge/test%20coverage-76%25-brightgreen.svg)](https://github.com/JubL/TimeRecorder)

A powerful and flexible Python tool for tracking and managing work hours with automatic overtime calculations, system boot time integration, and comprehensive reporting features.

## ✨ Features

- **🕐 Automatic Time Tracking**: Record work hours with start/end times and lunch breaks
- **⚡ System Boot Integration**: Automatically detect work start time from system boot
- **📊 Overtime Calculations**: Calculate overtime/undertime based on standard eight-hour work days (configurable)
- **📈 Weekly Reports**: Generate weekly work hour summaries with detailed analysis
- **🎨 Colored Output**: Visual feedback with color-coded overtime (green) and undertime (red)
- **📝 CSV Logbook**: Persistent storage of all time records in CSV format
- **🔧 Flexible Configuration**: YAML-based configuration system for easy customization
- **🌍 Holiday Support**: Automatic holiday detection
- **📱 Missing Day Detection**: Automatically add missing work days (weekends, holidays) to your logbook
- **🔄 Data Processing**: Automatic duplicate removal and data aggregation

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
⏰ Start Time: 07:00:00
⏰ End Time: 17:25:00
🍽️ Lunch Break: 60 minutes
⏱️ Work Duration: 9h 25m
📈 Status: OVERTIME (+1h 25m)

Weekly Summary:
==============
Week 30 (21.07.2025 - 27.07.2025)
Total Hours: 42h 15m
Standard Hours: 40h 0m
Overtime: +2h 15m

Recent Entries:
===============
Mon 25.07.2025 | 07:00-17:25 | 9h 25m | OVERTIME (+1h 25m)
Fri 22.07.2025 | 08:00-17:00 | 8h 0m  | ON TIME
Thu 21.07.2025 | 07:30-16:30 | 8h 0m  | ON TIME
```

## 🛠️ Development

### Project Structure

```
TimeRecorder/
├── main.py                # Main application entry point
├── config.yaml            # Configuration file (auto-generated)
├── src/                   # Source code
│   ├── arg_parser.py      # Command line argument parsing
│   ├── config_utils.py    # Configuration utilities
│   ├── logbook.py         # CSV logbook management
│   ├── logging_utils.py   # Logging configuration
│   └── time_recorder.py   # Core time tracking functionality
├── tests/                 # Test suite
│   ├── test_config_utils/
│   ├── test_logbook/
│   ├── test_logging_utils/
│   └── test_time_recorder/
└── pyproject.toml         # Project configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "unit"
pytest -m "integration"
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

### Export Options

Export your time records in various formats:

```yaml
output:
  export_format: "csv"  # Options: csv, json, excel
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

- **Issues**: [GitHub Issues](https://github.com/yourusername/TimeRecorder/issues)
- **Documentation**: [CONFIGURATION.md](CONFIGURATION.md)
- **Email**: jubin@lirawi.de

---

**Made with ⏰ by [Jubin Lirawi](https://github.com/yourusername)**
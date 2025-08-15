# TimeRecorder Formats Module

This module provides a flexible and extensible system for handling different file formats in TimeRecorder using the **Strategy Pattern** and a **Format Registry**.

## Overview

The formats system automatically selects the correct handler based on file extension, eliminating the need for switch statements or if-else chains. It's designed to be easily extensible - adding new formats requires minimal code changes.

## How It Works

### 1. Automatic Format Detection

The system automatically detects the file format based on the file extension:

```python
from src.formats import get_format_handler

# Automatically selects CSVHandler for .csv files
handler = get_format_handler(Path("logbook.csv"))

# Automatically selects JSONHandler for .json files
handler = get_format_handler(Path("logbook.json"))

# Automatically selects YAMLHandler for .yaml files
handler = get_format_handler(Path("logbook.yaml"))

# Automatically selects ExcelHandler for .xlsx files
handler = get_format_handler(Path("logbook.xlsx"))

# Automatically selects XMLHandler for .xml files
handler = get_format_handler(Path("logbook.xml"))
```

### 2. Format Registry

The `FORMAT_REGISTRY` maps file extensions to handler classes:

```python
FORMAT_REGISTRY = {
    ".csv": CSVHandler,
    ".xlsx": ExcelHandler,
    ".xls": ExcelHandler,
    ".json": JSONHandler,
    ".yaml": YAMLHandler,
    ".yml": YAMLHandler,
    ".xml": XMLHandler,
    ".parquet": ParquetHandler,
    ".pq": ParquetHandler,
}
```

### 3. Strategy Pattern

Each format handler implements the same interface (`BaseFormatHandler`), making them interchangeable:

```python
# All handlers have the same interface
handler.load(file_path)    # Load data from file
handler.save(df, file_path)  # Save data to file
handler.create_empty(file_path)  # Create empty file
```

## Supported Formats

Currently supported formats:

- **CSV** (`.csv`, `.txt`) - Semicolon-separated values with UTF-8 encoding
- **Excel** (`.xlsx`, `.xls`) - Microsoft Excel spreadsheet format
- **JSON** (`.json`) - JavaScript Object Notation
- **XML** (`.xml`) - Extensible Markup Language
- **YAML** (`.yaml`, `.yml`) - YAML Ain't Markup Language
- **Parquet** (`.parquet`, `.pq`) - Columnar storage format

## Usage in TimeRecorder

The Logbook class automatically uses the appropriate format handler:

```python
# In your config.yaml, specify the file path with desired extension
logging:
  log_path: "timereport_logbook.json"  # Will use JSON format

# The Logbook class automatically detects and uses the correct handler
logbook = Logbook(config)
df = logbook.load_logbook()  # Uses JSONHandler automatically
logbook.save_logbook(df)     # Uses JSONHandler automatically
```

## Adding New Formats

To add support for a new format (e.g., XML):

### 1. Create a Handler Class

```python
# src/formats/xml_handler.py
from pathlib import Path
import pandas as pd
from base import BaseFormatHandler

class XMLHandler(BaseFormatHandler):
    def load(self, file_path: Path) -> pd.DataFrame:
        # Implementation for loading XML
        pass

    def save(self, df: pd.DataFrame, file_path: Path) -> None:
        # Implementation for saving XML
        pass

    def create_empty(self, file_path: Path) -> None:
        # Implementation for creating empty XML
        pass
```

### 2. Register the Handler

```python
# In src/formats/__init__.py
from .xml_handler import XMLHandler

FORMAT_REGISTRY[".xml"] = XMLHandler
```

### 3. That's It!

The system will automatically use your new handler for `.xml` files:

```python
handler = get_format_handler(Path("logbook.xml"))  # Returns XMLHandler
```

## Benefits

### ✅ No Switch Statements
The system eliminates the need for complex conditional logic:

```python
# ❌ Old approach (not needed)
if file_path.suffix == ".csv":
    df = pd.read_csv(file_path)
elif file_path.suffix == ".json":
    df = pd.read_json(file_path)
elif file_path.suffix == ".yaml":
    df = pd.read_yaml(file_path)
# ... more conditions

# ✅ New approach
handler = get_format_handler(file_path)
df = handler.load(file_path)
```

### ✅ Easy Extension
Adding new formats doesn't require modifying existing code (Open/Closed Principle).

### ✅ Clean Separation
Each format handler is responsible only for its own format.

### ✅ Automatic Detection
Format is automatically detected based on file extension.

## API Reference

### Functions

- `get_format_handler(file_path: Path) -> BaseFormatHandler`
  - Returns the appropriate handler for the given file path
  - Raises `ValueError` if format is not supported

- `get_supported_formats() -> list[str]`
  - Returns list of supported file extensions

### BaseFormatHandler Interface

All format handlers must implement:

- `load(file_path: Path) -> pd.DataFrame`
- `save(df: pd.DataFrame, file_path: Path) -> None`
- `create_empty(file_path: Path) -> None`

## Example Usage

```python
from pathlib import Path
from src.formats import get_format_handler, get_supported_formats

# See what formats are supported
print(f"Supported formats: {get_supported_formats()}")

# Use any supported format
file_path = Path("my_logbook.json")
handler = get_format_handler(file_path)

# Load data
df = handler.load(file_path)

# Save data
handler.save(df, file_path)

# Create empty file
handler.create_empty(file_path)
```

## Testing

Run the demonstration script to see the system in action:

```bash
python examples/format_demo.py
```

This will show how different formats are handled automatically and demonstrate the extensibility of the system.

"""Tests for the format registry functionality in src.formats."""

import inspect
import pathlib
import time

import pytest

from src import formats


# Tests for get_supported_formats function
@pytest.mark.fast
def test_get_supported_formats_returns_list() -> None:
    """Test that get_supported_formats returns a list."""
    result = formats.get_supported_formats()
    assert isinstance(result, list)


@pytest.mark.fast
def test_get_supported_formats_contains_expected_extensions() -> None:
    """Test that get_supported_formats contains all expected file extensions."""
    expected_extensions = [
        ".csv",
        ".dat",
        ".txt",  # CSV formats
        ".xls",
        ".xlsx",  # Excel formats
        ".json",  # JSON format
        ".parquet",
        ".pq",  # Parquet formats
        ".xml",  # XML format
        ".yaml",
        ".yml",  # YAML formats
    ]

    result = formats.get_supported_formats()

    for extension in expected_extensions:
        assert extension in result, f"Expected extension {extension} not found in supported formats"


@pytest.mark.fast
def test_get_supported_formats_no_duplicates() -> None:
    """Test that get_supported_formats returns unique extensions."""
    result = formats.get_supported_formats()
    assert len(result) == len(set(result)), "Supported formats should not contain duplicates"


@pytest.mark.fast
def test_get_supported_formats_all_strings() -> None:
    """Test that all returned extensions are strings."""
    result = formats.get_supported_formats()
    for extension in result:
        assert isinstance(extension, str), f"Extension {extension} is not a string"


@pytest.mark.fast
def test_get_supported_formats_all_start_with_dot() -> None:
    """Test that all extensions start with a dot."""
    result = formats.get_supported_formats()
    for extension in result:
        assert extension.startswith("."), f"Extension {extension} does not start with a dot"


@pytest.mark.fast
def test_get_supported_formats_immutability() -> None:
    """Test that get_supported_formats returns a new list each time."""
    result1 = formats.get_supported_formats()
    result2 = formats.get_supported_formats()

    # Should be different list objects
    assert result1 is not result2
    # But same content
    assert result1 == result2


@pytest.mark.fast
def test_get_supported_formats_ordering() -> None:
    """Test that get_supported_formats returns extensions in consistent order."""
    result1 = formats.get_supported_formats()
    result2 = formats.get_supported_formats()

    # Order should be consistent (dict keys order)
    assert result1 == result2


@pytest.mark.fast
def test_get_supported_formats_performance() -> None:
    """Test that get_supported_formats is reasonably fast."""
    start_time = time.time()
    for _ in range(1000):
        formats.get_supported_formats()
    end_time = time.time()

    # Should complete 1000 calls in less than 1 second
    assert end_time - start_time < 1.0


# Tests for get_format_handler function
@pytest.mark.parametrize(
    ("file_extension", "expected_handler_name"),
    [
        (".csv", "CSVHandler"),
        (".dat", "CSVHandler"),
        (".txt", "CSVHandler"),
        (".xls", "ExcelHandler"),
        (".xlsx", "ExcelHandler"),
        (".json", "JSONHandler"),
        (".parquet", "ParquetHandler"),
        (".pq", "ParquetHandler"),
        (".xml", "XMLHandler"),
        (".yaml", "YAMLHandler"),
        (".yml", "YAMLHandler"),
    ],
)
@pytest.mark.fast
def test_get_format_handler_supported_extensions(
    file_extension: str,
    expected_handler_name: str,
) -> None:
    """Test that get_format_handler returns correct handler for supported extensions."""
    file_path = pathlib.Path(f"test_file{file_extension}")
    handler = formats.get_format_handler(file_path)

    assert handler.__class__.__name__ == expected_handler_name
    assert hasattr(handler, "load")
    assert hasattr(handler, "save")


@pytest.mark.parametrize(
    "file_extension",
    [
        ".CSV",  # Uppercase
        ".Csv",  # Mixed case
        ".cSV",  # Mixed case
    ],
)
@pytest.mark.fast
def test_get_format_handler_case_insensitive(file_extension: str) -> None:
    """Test that get_format_handler handles case-insensitive extensions."""
    file_path = pathlib.Path(f"test_file{file_extension}")
    handler = formats.get_format_handler(file_path)

    # Should return CSVHandler for all case variations of .csv
    assert handler.__class__.__name__ == "CSVHandler"


@pytest.mark.parametrize(
    "unsupported_extension",
    [
        ".pdf",
        ".doc",
        ".docx",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".7z",
        ".rar",
        ".mp3",
        ".mp4",
        ".avi",
        ".jpg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".svg",
        ".html",
        ".css",
        ".js",
        ".py",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".sql",
        ".db",
        ".sqlite",
        ".bak",
        ".tmp",
        ".log",
    ],
)
@pytest.mark.fast
def test_get_format_handler_unsupported_extensions(unsupported_extension: str) -> None:
    """Test that get_format_handler raises ValueError for unsupported extensions."""
    file_path = pathlib.Path(f"test_file{unsupported_extension}")

    with pytest.raises(ValueError, match="Unsupported file format") as exc_info:
        formats.get_format_handler(file_path)

    error_message = str(exc_info.value)
    assert "Unsupported file format" in error_message
    assert unsupported_extension.lower() in error_message
    assert "Supported formats" in error_message


@pytest.mark.fast
def test_get_format_handler_no_extension() -> None:
    """Test that get_format_handler raises ValueError for files without extension."""
    file_path = pathlib.Path("test_file_without_extension")

    with pytest.raises(ValueError, match="Unsupported file format") as exc_info:
        formats.get_format_handler(file_path)

    error_message = str(exc_info.value)
    assert "Unsupported file format" in error_message
    assert "Supported formats" in error_message


@pytest.mark.fast
def test_get_format_handler_empty_extension() -> None:
    """Test that get_format_handler raises ValueError for files with empty extension."""
    file_path = pathlib.Path("test_file.")

    with pytest.raises(ValueError, match="Unsupported file format") as exc_info:
        formats.get_format_handler(file_path)

    error_message = str(exc_info.value)
    assert "Unsupported file format" in error_message
    assert "Supported formats" in error_message


@pytest.mark.fast
def test_get_format_handler_error_message_includes_supported_formats() -> None:
    """Test that error message includes list of supported formats."""
    file_path = pathlib.Path("test_file.unsupported")
    supported_formats = formats.get_supported_formats()

    with pytest.raises(ValueError, match="Unsupported file format") as exc_info:
        formats.get_format_handler(file_path)

    error_message = str(exc_info.value)
    for format_ext in supported_formats:
        assert format_ext in error_message


@pytest.mark.fast
def test_get_format_handler_error_message_format() -> None:
    """Test that error messages follow expected format."""
    file_path = pathlib.Path("test.unsupported")

    with pytest.raises(ValueError, match="Unsupported file format") as exc_info:
        formats.get_format_handler(file_path)

    error_message = str(exc_info.value)

    # Should contain the unsupported extension
    assert ".unsupported" in error_message
    # Should mention supported formats
    assert "Supported formats" in error_message
    # Should list at least one supported format
    assert any(ext in error_message for ext in formats.get_supported_formats())


@pytest.mark.fast
def test_get_format_handler_returns_new_instance() -> None:
    """Test that get_format_handler returns a new instance each time."""
    file_path1 = pathlib.Path("test1.csv")
    file_path2 = pathlib.Path("test2.csv")

    handler1 = formats.get_format_handler(file_path1)
    handler2 = formats.get_format_handler(file_path2)

    # Should be different instances
    assert handler1 is not handler2
    # But same class
    assert handler1.__class__ == handler2.__class__


@pytest.mark.fast
def test_get_format_handler_with_complex_path() -> None:
    """Test that get_format_handler works with complex file paths."""
    file_path = pathlib.Path("/very/deep/nested/path/to/file.json")
    handler = formats.get_format_handler(file_path)

    assert handler.__class__.__name__ == "JSONHandler"


@pytest.mark.fast
def test_get_format_handler_with_relative_path() -> None:
    """Test that get_format_handler works with relative paths."""
    file_path = pathlib.Path("./relative/path/file.yaml")
    handler = formats.get_format_handler(file_path)

    assert handler.__class__.__name__ == "YAMLHandler"


@pytest.mark.fast
def test_get_format_handler_with_windows_path() -> None:
    """Test that get_format_handler works with Windows-style paths."""
    file_path = pathlib.Path("C:\\Users\\username\\Documents\\file.xlsx")
    handler = formats.get_format_handler(file_path)

    assert handler.__class__.__name__ == "ExcelHandler"


@pytest.mark.fast
def test_get_format_handler_with_special_characters() -> None:
    """Test that get_format_handler works with special characters in filename."""
    file_path = pathlib.Path("file with spaces and (parentheses).csv")
    handler = formats.get_format_handler(file_path)

    assert handler.__class__.__name__ == "CSVHandler"


@pytest.mark.fast
def test_get_format_handler_with_multiple_dots() -> None:
    """Test that get_format_handler works with filenames containing multiple dots."""
    file_path = pathlib.Path("file.name.with.multiple.dots.csv")
    handler = formats.get_format_handler(file_path)
    assert handler.__class__.__name__ == "CSVHandler"


@pytest.mark.fast
def test_get_format_handler_with_hidden_files() -> None:
    """Test that get_format_handler works with hidden files."""
    file_path = pathlib.Path(".hidden_file.json")
    handler = formats.get_format_handler(file_path)
    assert handler.__class__.__name__ == "JSONHandler"


@pytest.mark.fast
def test_get_format_handler_with_unicode_filenames() -> None:
    """Test that get_format_handler works with unicode filenames."""
    file_path = pathlib.Path("file_ümlaut_ñ_é.csv")
    handler = formats.get_format_handler(file_path)
    assert handler.__class__.__name__ == "CSVHandler"


@pytest.mark.fast
def test_get_format_handler_with_very_long_filename() -> None:
    """Test that get_format_handler works with very long filenames."""
    long_name = "a" * 1000 + ".csv"
    file_path = pathlib.Path(long_name)
    handler = formats.get_format_handler(file_path)
    assert handler.__class__.__name__ == "CSVHandler"


@pytest.mark.fast
def test_get_format_handler_with_numbers_in_extension() -> None:
    """Test that get_format_handler works with extensions containing numbers."""
    # This should fail since .csv1 is not supported
    file_path = pathlib.Path("test.csv1")
    with pytest.raises(ValueError, match="Unsupported file format"):
        formats.get_format_handler(file_path)


@pytest.mark.fast
def test_get_format_handler_with_path_object_methods() -> None:
    """Test that get_format_handler works with Path object methods."""
    # Test with Path.resolve() result
    file_path = pathlib.Path("test.csv").resolve()
    handler = formats.get_format_handler(file_path)
    assert handler.__class__.__name__ == "CSVHandler"


@pytest.mark.fast
def test_get_format_handler_performance() -> None:
    """Test that get_format_handler is reasonably fast."""
    file_path = pathlib.Path("test.csv")
    start_time = time.time()
    for _ in range(1000):
        formats.get_format_handler(file_path)
    end_time = time.time()

    # Should complete 1000 calls in less than 1 second
    assert end_time - start_time < 1.0


# Edge case tests
@pytest.mark.fast
def test_get_format_handler_with_none_path() -> None:
    """Test that get_format_handler handles None path gracefully."""
    with pytest.raises(AttributeError):
        formats.get_format_handler(None)


@pytest.mark.fast
def test_get_format_handler_case_sensitivity_edge_cases() -> None:
    """Test edge cases for case sensitivity handling."""
    # Test with mixed case extensions that don't exist
    file_path = pathlib.Path("test.PDF")
    with pytest.raises(ValueError, match="Unsupported file format"):
        formats.get_format_handler(file_path)


# Tests for format registry
@pytest.mark.fast
def test_format_registry_consistency() -> None:
    """Test that FORMAT_REGISTRY and get_supported_formats are consistent."""
    supported_formats = formats.get_supported_formats()

    # Check that all supported formats are in the registry
    for format_ext in supported_formats:
        assert format_ext in formats.FORMAT_REGISTRY

    # Check that all registry keys are in supported formats
    for format_ext in formats.FORMAT_REGISTRY:
        assert format_ext in supported_formats


@pytest.mark.fast
def test_format_registry_handler_types() -> None:
    """Test that all handlers in FORMAT_REGISTRY are valid handler classes."""
    from src.formats.base import BaseFormatHandler  # noqa: PLC0415

    for handler_class in formats.FORMAT_REGISTRY.values():
        # Check that it's a class
        assert isinstance(handler_class, type)
        # Check that it's a subclass of BaseFormatHandler
        assert issubclass(handler_class, BaseFormatHandler)
        # Check that it can be instantiated
        handler = handler_class()
        assert isinstance(handler, BaseFormatHandler)


@pytest.mark.fast
def test_format_registry_no_empty_extensions() -> None:
    """Test that FORMAT_REGISTRY doesn't contain empty extensions."""
    for format_ext in formats.FORMAT_REGISTRY:
        assert format_ext, "Empty extension found in FORMAT_REGISTRY"
        assert format_ext != ".", "Single dot extension found in FORMAT_REGISTRY"


@pytest.mark.fast
def test_format_registry_extensions_start_with_dot() -> None:
    """Test that all extensions in FORMAT_REGISTRY start with a dot."""
    for format_ext in formats.FORMAT_REGISTRY:
        assert format_ext.startswith("."), f"Extension {format_ext} does not start with a dot"


@pytest.mark.fast
def test_format_registry_extensions_lowercase() -> None:
    """Test that all extensions in FORMAT_REGISTRY are lowercase."""
    for format_ext in formats.FORMAT_REGISTRY:
        assert format_ext == format_ext.lower(), f"Extension {format_ext} is not lowercase"


@pytest.mark.fast
def test_format_registry_immutability() -> None:
    """Test that FORMAT_REGISTRY is not accidentally modified."""
    original_registry = formats.FORMAT_REGISTRY.copy()
    supported_formats = formats.get_supported_formats()

    # Modifying the returned list should not affect the registry
    supported_formats.append(".test")
    assert original_registry == formats.FORMAT_REGISTRY


@pytest.mark.fast
def test_format_registry_imports() -> None:
    """Test that all handler classes can be imported successfully."""
    # If we get here, all imports succeeded
    assert True


# Tests for handler interface
@pytest.mark.parametrize(
    "file_extension",
    [".csv", ".json", ".yaml", ".xlsx", ".xml", ".parquet"],
)
@pytest.mark.fast
def test_handler_interface_methods(file_extension: str) -> None:
    """Test that all handlers implement the required interface methods."""
    file_path = pathlib.Path(f"test_file{file_extension}")
    handler = formats.get_format_handler(file_path)

    # Check that all required methods exist
    required_methods = ["load", "save"]
    for method_name in required_methods:
        assert hasattr(handler, method_name), f"Handler missing method: {method_name}"
        method = getattr(handler, method_name)
        assert callable(method), f"Method {method_name} is not callable"


@pytest.mark.fast
def test_handler_method_signatures() -> None:
    """Test that handler methods have correct signatures."""
    # Test with CSV handler as representative
    file_path = pathlib.Path("test.csv")
    handler = formats.get_format_handler(file_path)

    # Check load method signature
    load_sig = inspect.signature(handler.load)
    assert "file_path" in load_sig.parameters

    # Check save method signature
    save_sig = inspect.signature(handler.save)
    assert "df" in save_sig.parameters
    assert "file_path" in save_sig.parameters

    # Check that methods have correct parameters
    load_sig = inspect.signature(handler.load)
    assert "file_path" in load_sig.parameters

    save_sig = inspect.signature(handler.save)
    assert "df" in save_sig.parameters
    assert "file_path" in save_sig.parameters

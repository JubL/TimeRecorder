"""Tests for the JSONHandler class in src.formats.json_handler."""

import inspect
import json
import pathlib
import time
from unittest.mock import patch

import pandas as pd
import pytest

from src.formats.base import BaseFormatHandler
from src.formats.json_handler import JSONHandler


@pytest.fixture
def json_handler() -> JSONHandler:
    """Fixture to create a JSONHandler instance."""
    return JSONHandler()


@pytest.fixture
def sample_json_data() -> pd.DataFrame:
    """Fixture to create sample data for JSON testing."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
            "department": ["HR", "IT", "Sales", "Marketing", "Finance"],
        },
    )


@pytest.fixture
def sample_json_records() -> list[dict]:
    """Fixture to create sample JSON records."""
    return [
        {"name": "Alice", "age": 25, "salary": 50000.0, "department": "HR"},
        {"name": "Bob", "age": 30, "salary": 60000.0, "department": "IT"},
        {"name": "Charlie", "age": 35, "salary": 70000.0, "department": "Sales"},
        {"name": "Diana", "age": 28, "salary": 55000.0, "department": "Marketing"},
        {"name": "Eve", "age": 32, "salary": 65000.0, "department": "Finance"},
    ]


@pytest.fixture
def sample_json_records_wrapper() -> dict:
    """Fixture to create sample JSON records wrapped in a records object."""
    return {
        "records": [
            {"name": "Alice", "age": 25, "salary": 50000.0, "department": "HR"},
            {"name": "Bob", "age": 30, "salary": 60000.0, "department": "IT"},
            {"name": "Charlie", "age": 35, "salary": 70000.0, "department": "Sales"},
            {"name": "Diana", "age": 28, "salary": 55000.0, "department": "Marketing"},
            {"name": "Eve", "age": 32, "salary": 65000.0, "department": "Finance"},
        ],
    }


# Tests for JSONHandler class
@pytest.mark.fast
def test_json_handler_instantiation() -> None:
    """Test that JSONHandler can be instantiated."""
    handler = JSONHandler()
    assert isinstance(handler, JSONHandler)


@pytest.mark.fast
def test_json_handler_inherits_from_base() -> None:
    """Test that JSONHandler inherits from BaseFormatHandler."""
    handler = JSONHandler()
    assert isinstance(handler, BaseFormatHandler)


@pytest.mark.fast
def test_json_handler_has_required_methods() -> None:
    """Test that JSONHandler has the required methods."""
    handler = JSONHandler()

    assert hasattr(handler, "load")
    assert hasattr(handler, "save")
    assert callable(handler.load)
    assert callable(handler.save)


# Tests for load method
@pytest.mark.fast
def test_load_method_is_static() -> None:
    """Test that the load method is static."""
    assert callable(JSONHandler.load)


@pytest.mark.fast
def test_load_successful_json_records_list(tmp_path: pathlib.Path, sample_json_records: list[dict]) -> None:
    """Test successful loading of JSON file with records list format."""
    file_path = tmp_path / "test.json"

    # Create JSON file with records list
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(sample_json_records, f, indent=2)

    # Load the file
    result = JSONHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_json_records)
    assert list(result.columns) == ["name", "age", "salary", "department"]


@pytest.mark.fast
def test_load_successful_json_records_wrapper(tmp_path: pathlib.Path, sample_json_records_wrapper: dict) -> None:
    """Test successful loading of JSON file with records wrapper format."""
    file_path = tmp_path / "test.json"

    # Create JSON file with records wrapper
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(sample_json_records_wrapper, f, indent=2)

    # Load the file
    result = JSONHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_json_records_wrapper["records"])
    assert list(result.columns) == ["name", "age", "salary", "department"]


@pytest.mark.fast
def test_load_empty_json_records_list(tmp_path: pathlib.Path) -> None:
    """Test loading JSON file with empty records list."""
    file_path = tmp_path / "empty.json"

    # Create JSON file with empty records list
    with file_path.open("w", encoding="utf-8") as f:
        json.dump([], f)

    # Load the file
    result = JSONHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


@pytest.mark.fast
def test_load_empty_json_records_wrapper(tmp_path: pathlib.Path) -> None:
    """Test loading JSON file with empty records wrapper."""
    file_path = tmp_path / "empty.json"

    # Create JSON file with empty records wrapper
    with file_path.open("w", encoding="utf-8") as f:
        json.dump({"records": []}, f)

    # Load the file
    result = JSONHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


@pytest.mark.fast
def test_load_json_with_different_data_types(tmp_path: pathlib.Path) -> None:
    """Test loading JSON file with various data types."""
    mixed_data = [
        {"string_col": "text1", "int_col": 1, "float_col": 1.1, "bool_col": True, "null_col": None},
        {"string_col": "text2", "int_col": 2, "float_col": 2.2, "bool_col": False, "null_col": None},
        {"string_col": "text3", "int_col": 3, "float_col": 3.3, "bool_col": True, "null_col": None},
    ]

    file_path = tmp_path / "mixed_types.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(mixed_data, f, indent=2)

    # Load the file
    result = JSONHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(mixed_data)
    assert list(result.columns) == ["string_col", "int_col", "float_col", "bool_col", "null_col"]


@pytest.mark.fast
def test_load_file_not_found() -> None:
    """Test that load raises FileNotFoundError for non-existent files."""
    file_path = pathlib.Path("nonexistent_file.json")

    with pytest.raises(FileNotFoundError, match="JSON file not found"):
        JSONHandler.load(file_path)


@pytest.mark.fast
def test_load_invalid_json_format(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for invalid JSON format."""
    # Create a file that's not valid JSON
    file_path = tmp_path / "invalid.json"
    file_path.write_text("This is not valid JSON")

    with pytest.raises(ValueError, match="Invalid JSON format"):
        JSONHandler.load(file_path)


@pytest.mark.fast
def test_load_invalid_json_structure(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for invalid JSON structure."""
    # Create JSON with invalid structure (not a list or records object)
    invalid_data = {"some_key": "some_value"}
    file_path = tmp_path / "invalid_structure.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(invalid_data, f)

    with pytest.raises(ValueError, match="Invalid JSON structure"):
        JSONHandler.load(file_path)


@pytest.mark.fast
def test_load_json_with_unicode_characters(tmp_path: pathlib.Path) -> None:
    """Test loading JSON file with unicode characters."""
    unicode_data = [
        {"text": "café", "numbers": 1},
        {"text": "naïve", "numbers": 2},
        {"text": "façade", "numbers": 3},
    ]

    file_path = tmp_path / "unicode.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(unicode_data, f, indent=2, ensure_ascii=False)

    # Load the file
    result = JSONHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(unicode_data)
    assert list(result.columns) == ["text", "numbers"]


# Tests for save method
@pytest.mark.fast
def test_save_method_is_static() -> None:
    """Test that the save method is static."""
    assert callable(JSONHandler.save)


@pytest.mark.fast
def test_save_successful_json_file(tmp_path: pathlib.Path, sample_json_data: pd.DataFrame) -> None:
    """Test successful saving of JSON files."""
    file_path = tmp_path / "test.json"

    # Save the DataFrame
    JSONHandler.save(sample_json_data, file_path)

    # Verify the file was created
    assert file_path.exists()
    assert file_path.stat().st_size > 0

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    # Should have records wrapper structure
    assert "records" in loaded_data
    assert isinstance(loaded_data["records"], list)
    assert len(loaded_data["records"]) == len(sample_json_data)


@pytest.mark.fast
def test_save_empty_dataframe(tmp_path: pathlib.Path) -> None:
    """Test saving an empty DataFrame."""
    empty_df = pd.DataFrame()
    file_path = tmp_path / "empty.json"

    # Save the empty DataFrame
    JSONHandler.save(empty_df, file_path)

    # Verify the file was created
    assert file_path.exists()

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert "records" in loaded_data
    assert loaded_data["records"] == []


@pytest.mark.fast
def test_save_dataframe_with_different_data_types(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with various data types."""
    mixed_df = pd.DataFrame(
        {
            "string_col": ["text1", "text2", "text3"],
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "bool_col": [True, False, True],
            "null_col": [None, None, None],
        },
    )

    file_path = tmp_path / "mixed_types.json"

    # Save the DataFrame
    JSONHandler.save(mixed_df, file_path)

    # Verify the file was created
    assert file_path.exists()

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(mixed_df)


@pytest.mark.fast
def test_save_large_dataframe(tmp_path: pathlib.Path) -> None:
    """Test saving a large DataFrame."""
    # Create a larger DataFrame
    large_df = pd.DataFrame(
        {
            "col1": range(100),
            "col2": [f"text_{i}" for i in range(100)],
            "col3": [i * 1.5 for i in range(100)],
        },
    )

    file_path = tmp_path / "large.json"

    # Save the DataFrame
    JSONHandler.save(large_df, file_path)

    # Verify the file was created
    assert file_path.exists()
    assert file_path.stat().st_size > 0

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(large_df)


@pytest.mark.fast
def test_save_permission_error(tmp_path: pathlib.Path, sample_json_data: pd.DataFrame) -> None:
    """Test that save raises PermissionError for permission issues."""
    # Create a file that we can't write to (simulate permission error)
    file_path = tmp_path / "readonly.json"
    file_path.touch()
    file_path.chmod(0o444)  # Read-only

    try:
        with pytest.raises(PermissionError, match="Permission denied"):
            JSONHandler.save(sample_json_data, file_path)
    finally:
        # Restore permissions for cleanup
        file_path.chmod(0o666)


@pytest.mark.fast
def test_save_os_error(tmp_path: pathlib.Path, sample_json_data: pd.DataFrame) -> None:
    """Test that save raises OSError for OS-level errors."""
    # Create a directory that doesn't exist
    file_path = tmp_path / "nonexistent" / "test.json"

    with pytest.raises(OSError, match="OS error"):
        JSONHandler.save(sample_json_data, file_path)


@pytest.mark.fast
def test_save_with_unicode_characters(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with unicode characters."""
    unicode_df = pd.DataFrame(
        {
            "text": ["café", "naïve", "façade", "résumé", "über"],
            "numbers": [1, 2, 3, 4, 5],
        },
    )

    file_path = tmp_path / "unicode.json"

    # Save the DataFrame
    JSONHandler.save(unicode_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(unicode_df)


@pytest.mark.fast
def test_save_with_nan_values(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with NaN values."""
    nan_df = pd.DataFrame(
        {
            "col1": [1, 2, float("nan"), 4, 5],
            "col2": ["a", "b", None, "d", "e"],
            "col3": [1.1, 2.2, float("nan"), 4.4, 5.5],
        },
    )

    file_path = tmp_path / "nan_values.json"

    # Save the DataFrame
    JSONHandler.save(nan_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(nan_df)


@pytest.mark.fast
def test_save_with_datetime_columns(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with datetime columns."""
    # Use string format directly to avoid JSON serialization issues
    datetime_df = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "datetime": ["2024-01-01 10:30:00", "2024-01-02 14:45:00", "2024-01-03 09:15:00"],
            "value": [1, 2, 3],
        },
    )

    file_path = tmp_path / "datetime.json"

    # Save the DataFrame
    JSONHandler.save(datetime_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(datetime_df)


# Integration tests
@pytest.mark.fast
def test_load_save_roundtrip(tmp_path: pathlib.Path, sample_json_data: pd.DataFrame) -> None:
    """Test that data can be saved and loaded back correctly."""
    file_path = tmp_path / "roundtrip.json"

    # Save the DataFrame
    JSONHandler.save(sample_json_data, file_path)

    # Load it back
    loaded_df = JSONHandler.load(file_path)

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_json_data, check_dtype=False)


@pytest.mark.fast
def test_load_save_with_sample_df_fixture(tmp_path: pathlib.Path, sample_df: pd.DataFrame) -> None:
    """Test load/save with the sample_df fixture from conftest."""
    file_path = tmp_path / "sample_df.json"

    # Save the DataFrame
    JSONHandler.save(sample_df, file_path)

    # Load it back
    loaded_df = JSONHandler.load(file_path)

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_df, check_dtype=False)


@pytest.mark.fast
def test_load_save_with_sample_logbook_df_fixture(tmp_path: pathlib.Path, sample_logbook_df: pd.DataFrame) -> None:
    """Test load/save with the sample_logbook_df fixture from conftest."""
    file_path = tmp_path / "sample_logbook_df.json"

    # Save the DataFrame
    JSONHandler.save(sample_logbook_df, file_path)

    # Load it back
    loaded_df = JSONHandler.load(file_path)

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_logbook_df, check_dtype=False)


# Edge case tests
@pytest.mark.fast
def test_save_to_existing_file_overwrites(tmp_path: pathlib.Path, sample_json_data: pd.DataFrame) -> None:
    """Test that saving to an existing file overwrites it."""
    file_path = tmp_path / "overwrite.json"

    # Create initial content
    initial_df = pd.DataFrame({"col1": [1, 2, 3]})
    JSONHandler.save(initial_df, file_path)

    # Save new content
    JSONHandler.save(sample_json_data, file_path)

    # Verify the new content is there
    loaded_df = JSONHandler.load(file_path)
    pd.testing.assert_frame_equal(loaded_df, sample_json_data, check_dtype=False)


@pytest.mark.fast
def test_save_with_special_characters_in_filename(tmp_path: pathlib.Path, sample_json_data: pd.DataFrame) -> None:
    """Test saving with special characters in filename."""
    file_path = tmp_path / "file with spaces and (parentheses).json"

    # Save the DataFrame
    JSONHandler.save(sample_json_data, file_path)

    # Verify the file was created
    assert file_path.exists()

    # Verify the content by loading it back
    loaded_df = JSONHandler.load(file_path)
    pd.testing.assert_frame_equal(loaded_df, sample_json_data, check_dtype=False)


@pytest.mark.fast
def test_save_with_nested_structures(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with nested structures (should be serializable)."""
    nested_df = pd.DataFrame(
        {
            "simple_col": [1, 2, 3],
            "list_col": [[1, 2], [3, 4], [5, 6]],
            "dict_col": [{"a": 1}, {"b": 2}, {"c": 3}],
        },
    )

    file_path = tmp_path / "nested.json"

    # Save the DataFrame
    JSONHandler.save(nested_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(nested_df)


# Tests for method signatures
@pytest.mark.fast
def test_handler_method_signatures() -> None:
    """Test that handler methods have correct signatures."""
    # Check load method signature
    load_sig = inspect.signature(JSONHandler.load)
    assert "file_path" in load_sig.parameters

    # Check save method signature
    save_sig = inspect.signature(JSONHandler.save)
    assert "df" in save_sig.parameters
    assert "file_path" in save_sig.parameters


# Tests for error message content
@pytest.mark.fast
def test_load_error_message_content(tmp_path: pathlib.Path) -> None:
    """Test that error messages contain expected content."""
    file_path = tmp_path / "test.json"
    file_path.touch()

    with pytest.raises(ValueError, match="Invalid JSON format") as exc_info:
        JSONHandler.load(file_path)

    error_message = str(exc_info.value)
    assert "Invalid JSON format" in error_message


@pytest.mark.fast
def test_save_error_message_content(sample_json_data: pd.DataFrame, tmp_path: pathlib.Path) -> None:
    """Test that save error messages contain expected content."""
    file_path = tmp_path / "test.json"

    # Mock the open function to raise PermissionError
    with patch("pathlib.Path.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(PermissionError) as exc_info:
            JSONHandler.save(sample_json_data, file_path)

        error_message = str(exc_info.value)
        assert "Permission denied when saving JSON to" in error_message


# Tests for JSON structure handling
@pytest.mark.fast
def test_load_json_with_extra_fields_in_wrapper(tmp_path: pathlib.Path) -> None:
    """Test loading JSON with extra fields in the wrapper object."""
    data_with_extra = {
        "records": [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
        ],
        "metadata": {"version": "1.0", "created": "2024-01-01"},
        "extra_field": "should be ignored",
    }

    file_path = tmp_path / "extra_fields.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data_with_extra, f, indent=2)

    # Load the file
    result = JSONHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == ["name", "age"]


@pytest.mark.fast
def test_load_json_with_missing_records_key(tmp_path: pathlib.Path) -> None:
    """Test loading JSON with missing records key in wrapper."""
    data_without_records = {
        "data": [{"name": "Alice", "age": 25}],
        "metadata": {"version": "1.0"},
    }

    file_path = tmp_path / "no_records.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data_without_records, f, indent=2)

    with pytest.raises(ValueError, match="Invalid JSON structure"):
        JSONHandler.load(file_path)


# Performance tests
@pytest.mark.fast
def test_save_performance(tmp_path: pathlib.Path) -> None:
    """Test that save is reasonably fast."""
    # Create a moderately sized DataFrame
    df = pd.DataFrame(
        {
            "col1": range(100),
            "col2": [f"text_{i}" for i in range(100)],
            "col3": [i * 1.5 for i in range(100)],
        },
    )

    file_path = tmp_path / "performance.json"

    start_time = time.time()
    JSONHandler.save(df, file_path)
    end_time = time.time()

    # Should complete in less than 5 seconds
    assert end_time - start_time < 5.0


@pytest.mark.fast
def test_load_performance(tmp_path: pathlib.Path) -> None:
    """Test that load is reasonably fast."""
    # Create a moderately sized DataFrame and save it
    df = pd.DataFrame(
        {
            "col1": range(100),
            "col2": [f"text_{i}" for i in range(100)],
            "col3": [i * 1.5 for i in range(100)],
        },
    )

    file_path = tmp_path / "performance.json"
    JSONHandler.save(df, file_path)

    start_time = time.time()
    JSONHandler.load(file_path)
    end_time = time.time()

    # Should complete in less than 5 seconds
    assert end_time - start_time < 5.0

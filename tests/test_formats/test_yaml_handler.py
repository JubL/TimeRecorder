"""Tests for the YAMLHandler class in src.formats.yaml_handler."""

import inspect
import pathlib
import time
from unittest.mock import patch

import pandas as pd
import pytest
import yaml

from src.formats.base import BaseFormatHandler
from src.formats.yaml_handler import YAMLHandler


@pytest.fixture
def yaml_handler() -> YAMLHandler:
    """Fixture to create a YAMLHandler instance."""
    return YAMLHandler()


@pytest.fixture
def sample_yaml_data() -> pd.DataFrame:
    """Fixture to create sample data for YAML testing."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
            "department": ["HR", "IT", "Sales", "Marketing", "Finance"],
        },
    )


@pytest.fixture
def sample_yaml_records() -> list[dict]:
    """Fixture to create sample YAML records."""
    return [
        {"name": "Alice", "age": 25, "salary": 50000.0, "department": "HR"},
        {"name": "Bob", "age": 30, "salary": 60000.0, "department": "IT"},
        {"name": "Charlie", "age": 35, "salary": 70000.0, "department": "Sales"},
        {"name": "Diana", "age": 28, "salary": 55000.0, "department": "Marketing"},
        {"name": "Eve", "age": 32, "salary": 65000.0, "department": "Finance"},
    ]


@pytest.fixture
def sample_yaml_records_wrapper() -> dict:
    """Fixture to create sample YAML records wrapped in a records object."""
    return {
        "records": [
            {"name": "Alice", "age": 25, "salary": 50000.0, "department": "HR"},
            {"name": "Bob", "age": 30, "salary": 60000.0, "department": "IT"},
            {"name": "Charlie", "age": 35, "salary": 70000.0, "department": "Sales"},
            {"name": "Diana", "age": 28, "salary": 55000.0, "department": "Marketing"},
            {"name": "Eve", "age": 32, "salary": 65000.0, "department": "Finance"},
        ],
    }


# Tests for YAMLHandler class
@pytest.mark.fast
def test_yaml_handler_instantiation() -> None:
    """Test that YAMLHandler can be instantiated."""
    handler = YAMLHandler()
    assert isinstance(handler, YAMLHandler)


@pytest.mark.fast
def test_yaml_handler_inherits_from_base() -> None:
    """Test that YAMLHandler inherits from BaseFormatHandler."""
    handler = YAMLHandler()
    assert isinstance(handler, BaseFormatHandler)


@pytest.mark.fast
def test_yaml_handler_has_required_methods() -> None:
    """Test that YAMLHandler has the required methods."""
    handler = YAMLHandler()

    assert hasattr(handler, "load")
    assert hasattr(handler, "save")
    assert callable(handler.load)
    assert callable(handler.save)


# Tests for load method
@pytest.mark.fast
def test_load_method_is_static() -> None:
    """Test that the load method is static."""
    assert callable(YAMLHandler.load)


@pytest.mark.fast
def test_load_successful_yaml_records_list(tmp_path: pathlib.Path, sample_yaml_records: list[dict]) -> None:
    """Test successful loading of YAML file with records list format."""
    file_path = tmp_path / "test.yaml"

    # Create YAML file with records list
    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(sample_yaml_records, f, default_flow_style=False, allow_unicode=True)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_yaml_records)
    # Note: pandas sorts columns alphabetically when creating DataFrame from dict
    assert sorted(result.columns) == sorted(["name", "age", "salary", "department"])


@pytest.mark.fast
def test_load_successful_yaml_records_wrapper(tmp_path: pathlib.Path, sample_yaml_records_wrapper: dict) -> None:
    """Test successful loading of YAML file with records wrapper format."""
    file_path = tmp_path / "test.yaml"

    # Create YAML file with records wrapper
    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(sample_yaml_records_wrapper, f, default_flow_style=False, allow_unicode=True)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_yaml_records_wrapper["records"])
    # Note: pandas sorts columns alphabetically when creating DataFrame from dict
    assert sorted(result.columns) == sorted(["name", "age", "salary", "department"])


@pytest.mark.fast
def test_load_empty_yaml_records_list(tmp_path: pathlib.Path) -> None:
    """Test loading YAML file with empty records list."""
    file_path = tmp_path / "empty.yaml"

    # Create YAML file with empty records list
    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump([], f, default_flow_style=False)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


@pytest.mark.fast
def test_load_empty_yaml_records_wrapper(tmp_path: pathlib.Path) -> None:
    """Test loading YAML file with empty records wrapper."""
    file_path = tmp_path / "empty.yaml"

    # Create YAML file with empty records wrapper
    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump({"records": []}, f, default_flow_style=False)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


@pytest.mark.fast
def test_load_yaml_with_different_data_types(tmp_path: pathlib.Path) -> None:
    """Test loading YAML file with various data types."""
    mixed_data = [
        {"string_col": "text1", "int_col": 1, "float_col": 1.1, "bool_col": True, "null_col": None},
        {"string_col": "text2", "int_col": 2, "float_col": 2.2, "bool_col": False, "null_col": None},
        {"string_col": "text3", "int_col": 3, "float_col": 3.3, "bool_col": True, "null_col": None},
    ]

    file_path = tmp_path / "mixed_types.yaml"

    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(mixed_data, f, default_flow_style=False, allow_unicode=True)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(mixed_data)
    # Note: pandas sorts columns alphabetically when creating DataFrame from dict
    assert sorted(result.columns) == sorted(["string_col", "int_col", "float_col", "bool_col", "null_col"])


@pytest.mark.fast
def test_load_file_not_found() -> None:
    """Test that load raises FileNotFoundError for non-existent files."""
    file_path = pathlib.Path("nonexistent_file.yaml")

    with pytest.raises(FileNotFoundError, match="YAML file not found"):
        YAMLHandler.load(file_path)


@pytest.mark.fast
def test_load_invalid_yaml_format(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for invalid YAML format."""
    # Create a file that's not valid YAML
    file_path = tmp_path / "invalid.yaml"
    file_path.write_text("This is not valid YAML: [invalid syntax")

    with pytest.raises(ValueError, match="Invalid YAML format"):
        YAMLHandler.load(file_path)


@pytest.mark.fast
def test_load_invalid_yaml_structure(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for invalid YAML structure."""
    # Create YAML with invalid structure (not a list or records object)
    invalid_data = {"some_key": "some_value"}
    file_path = tmp_path / "invalid_structure.yaml"

    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(invalid_data, f, default_flow_style=False)

    with pytest.raises(ValueError, match="Invalid YAML structure"):
        YAMLHandler.load(file_path)


@pytest.mark.fast
def test_load_yaml_with_unicode_characters(tmp_path: pathlib.Path) -> None:
    """Test loading YAML file with unicode characters."""
    unicode_data = [
        {"text": "café", "numbers": 1},
        {"text": "naïve", "numbers": 2},
        {"text": "façade", "numbers": 3},
    ]

    file_path = tmp_path / "unicode.yaml"

    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(unicode_data, f, default_flow_style=False, allow_unicode=True)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(unicode_data)
    # Note: pandas sorts columns alphabetically when creating DataFrame from dict
    assert sorted(result.columns) == sorted(["text", "numbers"])


# Tests for save method
@pytest.mark.fast
def test_save_method_is_static() -> None:
    """Test that the save method is static."""
    assert callable(YAMLHandler.save)


@pytest.mark.fast
def test_save_successful_yaml_file(tmp_path: pathlib.Path, sample_yaml_data: pd.DataFrame) -> None:
    """Test successful saving of YAML files."""
    file_path = tmp_path / "test.yaml"

    # Save the DataFrame
    YAMLHandler.save(sample_yaml_data, file_path)

    # Verify the file was created
    assert file_path.exists()
    assert file_path.stat().st_size > 0

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    # Should have columns and records structure
    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert isinstance(loaded_data["records"], list)
    assert len(loaded_data["records"]) == len(sample_yaml_data)
    assert loaded_data["columns"] == list(sample_yaml_data.columns)


@pytest.mark.fast
def test_save_empty_dataframe(tmp_path: pathlib.Path) -> None:
    """Test saving an empty DataFrame."""
    empty_df = pd.DataFrame()
    file_path = tmp_path / "empty.yaml"

    # Save the empty DataFrame
    YAMLHandler.save(empty_df, file_path)

    # Verify the file was created
    assert file_path.exists()

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert loaded_data["records"] == []
    assert loaded_data["columns"] == []


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

    file_path = tmp_path / "mixed_types.yaml"

    # Save the DataFrame
    YAMLHandler.save(mixed_df, file_path)

    # Verify the file was created
    assert file_path.exists()

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(mixed_df)
    assert loaded_data["columns"] == list(mixed_df.columns)


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

    file_path = tmp_path / "large.yaml"

    # Save the DataFrame
    YAMLHandler.save(large_df, file_path)

    # Verify the file was created
    assert file_path.exists()
    assert file_path.stat().st_size > 0

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(large_df)
    assert loaded_data["columns"] == list(large_df.columns)


@pytest.mark.fast
def test_save_permission_error(tmp_path: pathlib.Path, sample_yaml_data: pd.DataFrame) -> None:
    """Test that save raises PermissionError for permission issues."""
    # Create a file that we can't write to (simulate permission error)
    file_path = tmp_path / "readonly.yaml"
    file_path.touch()
    file_path.chmod(0o444)  # Read-only

    try:
        with pytest.raises(PermissionError, match="Permission denied"):
            YAMLHandler.save(sample_yaml_data, file_path)
    finally:
        # Restore permissions for cleanup
        file_path.chmod(0o666)


@pytest.mark.fast
def test_save_os_error(tmp_path: pathlib.Path, sample_yaml_data: pd.DataFrame) -> None:
    """Test that save raises OSError for OS-level errors."""
    # Create a directory that doesn't exist
    file_path = tmp_path / "nonexistent" / "test.yaml"

    with pytest.raises(OSError, match="OS error"):
        YAMLHandler.save(sample_yaml_data, file_path)


@pytest.mark.fast
def test_save_with_unicode_characters(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with unicode characters."""
    unicode_df = pd.DataFrame(
        {
            "text": ["café", "naïve", "façade", "résumé", "über"],
            "numbers": [1, 2, 3, 4, 5],
        },
    )

    file_path = tmp_path / "unicode.yaml"

    # Save the DataFrame
    YAMLHandler.save(unicode_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(unicode_df)
    assert loaded_data["columns"] == list(unicode_df.columns)


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

    file_path = tmp_path / "nan_values.yaml"

    # Save the DataFrame
    YAMLHandler.save(nan_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(nan_df)
    assert loaded_data["columns"] == list(nan_df.columns)


@pytest.mark.fast
def test_save_with_datetime_columns(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with datetime columns."""
    # Use string format directly to avoid YAML serialization issues
    datetime_df = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "datetime": ["2024-01-01 10:30:00", "2024-01-02 14:45:00", "2024-01-03 09:15:00"],
            "value": [1, 2, 3],
        },
    )

    file_path = tmp_path / "datetime.yaml"

    # Save the DataFrame
    YAMLHandler.save(datetime_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(datetime_df)
    assert loaded_data["columns"] == list(datetime_df.columns)


# Integration tests
@pytest.mark.fast
def test_load_save_roundtrip(tmp_path: pathlib.Path, sample_yaml_data: pd.DataFrame) -> None:
    """Test that data can be saved and loaded back correctly."""
    file_path = tmp_path / "roundtrip.yaml"

    # Save the DataFrame
    YAMLHandler.save(sample_yaml_data, file_path)

    # Load it back
    loaded_df = YAMLHandler.load(file_path)

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_yaml_data, check_dtype=False)


@pytest.mark.fast
def test_load_save_with_sample_df_fixture(tmp_path: pathlib.Path, sample_df: pd.DataFrame) -> None:
    """Test load/save with the sample_df fixture from conftest."""
    file_path = tmp_path / "sample_df.yaml"

    # Save the DataFrame
    YAMLHandler.save(sample_df, file_path)

    # Load it back
    loaded_df = YAMLHandler.load(file_path)

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_df, check_dtype=False)


@pytest.mark.fast
def test_load_save_with_sample_logbook_df_fixture(tmp_path: pathlib.Path, sample_logbook_df: pd.DataFrame) -> None:
    """Test load/save with the sample_logbook_df fixture from conftest."""
    file_path = tmp_path / "sample_logbook_df.yaml"

    # Save the DataFrame
    YAMLHandler.save(sample_logbook_df, file_path)

    # Load it back
    loaded_df = YAMLHandler.load(file_path)

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_logbook_df, check_dtype=False)


# Edge case tests
@pytest.mark.fast
def test_save_to_existing_file_overwrites(tmp_path: pathlib.Path, sample_yaml_data: pd.DataFrame) -> None:
    """Test that saving to an existing file overwrites it."""
    file_path = tmp_path / "overwrite.yaml"

    # Create initial content
    initial_df = pd.DataFrame({"col1": [1, 2, 3]})
    YAMLHandler.save(initial_df, file_path)

    # Save new content
    YAMLHandler.save(sample_yaml_data, file_path)

    # Verify the new content is there
    loaded_df = YAMLHandler.load(file_path)
    pd.testing.assert_frame_equal(loaded_df, sample_yaml_data, check_dtype=False)


@pytest.mark.fast
def test_save_with_special_characters_in_filename(tmp_path: pathlib.Path, sample_yaml_data: pd.DataFrame) -> None:
    """Test saving with special characters in filename."""
    file_path = tmp_path / "file with spaces and (parentheses).yaml"

    # Save the DataFrame
    YAMLHandler.save(sample_yaml_data, file_path)

    # Verify the file was created
    assert file_path.exists()

    # Verify the content by loading it back
    loaded_df = YAMLHandler.load(file_path)
    pd.testing.assert_frame_equal(loaded_df, sample_yaml_data, check_dtype=False)


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

    file_path = tmp_path / "nested.yaml"

    # Save the DataFrame
    YAMLHandler.save(nested_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(nested_df)
    assert loaded_data["columns"] == list(nested_df.columns)


# Tests for method signatures
@pytest.mark.fast
def test_handler_method_signatures() -> None:
    """Test that handler methods have correct signatures."""
    # Check load method signature
    load_sig = inspect.signature(YAMLHandler.load)
    assert "file_path" in load_sig.parameters

    # Check save method signature
    save_sig = inspect.signature(YAMLHandler.save)
    assert "df" in save_sig.parameters
    assert "file_path" in save_sig.parameters


# Tests for error message content
@pytest.mark.fast
def test_load_error_message_content(tmp_path: pathlib.Path) -> None:
    """Test that error messages contain expected content."""
    file_path = tmp_path / "test.yaml"
    file_path.touch()

    with pytest.raises(ValueError, match="Invalid YAML structure") as exc_info:
        YAMLHandler.load(file_path)

    error_message = str(exc_info.value)
    assert "Invalid YAML structure" in error_message


@pytest.mark.fast
def test_save_error_message_content(sample_yaml_data: pd.DataFrame) -> None:
    """Test that save error messages contain expected content."""
    file_path = pathlib.Path("test.yaml")

    # Mock the open function to raise PermissionError
    with patch("pathlib.Path.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(PermissionError) as exc_info:
            YAMLHandler.save(sample_yaml_data, file_path)

        error_message = str(exc_info.value)
        assert "Permission denied when saving YAML to" in error_message


# Tests for YAML structure handling
@pytest.mark.fast
def test_load_yaml_with_extra_fields_in_wrapper(tmp_path: pathlib.Path) -> None:
    """Test loading YAML with extra fields in the wrapper object."""
    data_with_extra = {
        "records": [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
        ],
        "metadata": {"version": "1.0", "created": "2024-01-01"},
        "extra_field": "should be ignored",
    }

    file_path = tmp_path / "extra_fields.yaml"

    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data_with_extra, f, default_flow_style=False, allow_unicode=True)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    # Note: pandas sorts columns alphabetically when creating DataFrame from dict
    assert sorted(result.columns) == sorted(["name", "age"])


@pytest.mark.fast
def test_load_yaml_with_missing_records_key(tmp_path: pathlib.Path) -> None:
    """Test loading YAML with missing records key in wrapper."""
    data_without_records = {
        "data": [{"name": "Alice", "age": 25}],
        "metadata": {"version": "1.0"},
    }

    file_path = tmp_path / "no_records.yaml"

    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data_without_records, f, default_flow_style=False, allow_unicode=True)

    with pytest.raises(ValueError, match="Invalid YAML structure"):
        YAMLHandler.load(file_path)


# Tests for YAML-specific features
@pytest.mark.fast
def test_save_preserves_column_order(tmp_path: pathlib.Path) -> None:
    """Test that save preserves the order of columns."""
    # Create DataFrame with specific column order
    df = pd.DataFrame(
        {
            "z_col": [3, 6, 9],
            "a_col": [1, 4, 7],
            "m_col": [2, 5, 8],
        },
    )

    file_path = tmp_path / "column_order.yaml"

    # Save the DataFrame
    YAMLHandler.save(df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert loaded_data["columns"] == ["z_col", "a_col", "m_col"]


@pytest.mark.fast
def test_save_with_complex_yaml_structures(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with complex YAML-compatible structures."""
    complex_df = pd.DataFrame(
        {
            "simple": [1, 2, 3],
            "list_values": [[1, 2], [3, 4], [5, 6]],
            "dict_values": [{"a": 1, "b": 2}, {"c": 3, "d": 4}, {"e": 5, "f": 6}],
            "nested": [{"x": {"y": 1}}, {"x": {"y": 2}}, {"x": {"y": 3}}],
        },
    )

    file_path = tmp_path / "complex.yaml"

    # Save the DataFrame
    YAMLHandler.save(complex_df, file_path)

    # Verify the content by loading it back
    with file_path.open("r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

    assert "columns" in loaded_data
    assert "records" in loaded_data
    assert len(loaded_data["records"]) == len(complex_df)
    assert loaded_data["columns"] == list(complex_df.columns)


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

    file_path = tmp_path / "performance.yaml"

    start_time = time.time()
    YAMLHandler.save(df, file_path)
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

    file_path = tmp_path / "performance.yaml"
    YAMLHandler.save(df, file_path)

    start_time = time.time()
    YAMLHandler.load(file_path)
    end_time = time.time()

    # Should complete in less than 5 seconds
    assert end_time - start_time < 5.0


# Tests for YAML-specific error handling
@pytest.mark.fast
def test_load_yaml_with_anchor_references(tmp_path: pathlib.Path) -> None:
    """Test loading YAML with anchor references (should work with safe_load)."""
    yaml_with_anchors = """
records:
  - name: &name1 Alice
    age: 25
  - name: *name1
    age: 30
  - name: Bob
    age: 35
"""

    file_path = tmp_path / "anchors.yaml"
    file_path.write_text(yaml_with_anchors)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    # Note: pandas sorts columns alphabetically when creating DataFrame from dict
    assert sorted(result.columns) == sorted(["name", "age"])


@pytest.mark.fast
def test_load_yaml_with_comments(tmp_path: pathlib.Path) -> None:
    """Test loading YAML with comments."""
    yaml_with_comments = """
# This is a comment
records:
  - name: Alice  # Another comment
    age: 25
  - name: Bob
    age: 30
"""

    file_path = tmp_path / "comments.yaml"
    file_path.write_text(yaml_with_comments)

    # Load the file
    result = YAMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    # Note: pandas sorts columns alphabetically when creating DataFrame from dict
    assert sorted(result.columns) == sorted(["name", "age"])


@pytest.mark.fast
def test_save_with_yaml_flow_style_disabled(tmp_path: pathlib.Path, sample_yaml_data: pd.DataFrame) -> None:
    """Test that save uses block style (not flow style) for better readability."""
    file_path = tmp_path / "flow_style.yaml"

    # Save the DataFrame
    YAMLHandler.save(sample_yaml_data, file_path)

    # Read the raw content to check format
    content = file_path.read_text(encoding="utf-8")

    # Should use block style (not flow style)
    assert "columns:" in content
    assert "records:" in content
    assert "- name:" in content  # Block style list items
    assert not content.strip().startswith("{")  # Not flow style

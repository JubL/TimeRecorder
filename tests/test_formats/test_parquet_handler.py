"""Tests for the ParquetHandler class in src.formats.parquet_handler."""

import inspect
import pathlib
import time
from unittest.mock import patch

import pandas as pd
import pytest

from src.formats.base import BaseFormatHandler
from src.formats.parquet_handler import ParquetHandler


@pytest.fixture
def parquet_handler() -> ParquetHandler:
    """Fixture to create a ParquetHandler instance."""
    return ParquetHandler()


@pytest.fixture
def sample_parquet_data() -> pd.DataFrame:
    """Fixture to create sample data for Parquet testing."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
            "department": ["HR", "IT", "Sales", "Marketing", "Finance"],
        },
    )


# Tests for ParquetHandler class
@pytest.mark.fast
def test_parquet_handler_instantiation() -> None:
    """Test that ParquetHandler can be instantiated."""
    handler = ParquetHandler()
    assert isinstance(handler, ParquetHandler)


@pytest.mark.fast
def test_parquet_handler_inherits_from_base() -> None:
    """Test that ParquetHandler inherits from BaseFormatHandler."""
    handler = ParquetHandler()
    assert isinstance(handler, BaseFormatHandler)


@pytest.mark.fast
def test_parquet_handler_has_required_methods() -> None:
    """Test that ParquetHandler has the required methods."""
    handler = ParquetHandler()

    assert hasattr(handler, "load")
    assert hasattr(handler, "save")
    assert callable(handler.load)
    assert callable(handler.save)


# Tests for load method
@pytest.mark.fast
def test_load_method_is_static() -> None:
    """Test that the load method is static."""
    assert callable(ParquetHandler.load)


@pytest.mark.fast
def test_load_file_not_found() -> None:
    """Test that load raises FileNotFoundError for non-existent files."""
    file_path = pathlib.Path("nonexistent_file.parquet")

    with pytest.raises(FileNotFoundError, match="Parquet file not found"):
        ParquetHandler.load(file_path)


@pytest.mark.fast
def test_load_invalid_parquet_format(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for invalid Parquet format."""
    # Create a file that's not a valid Parquet file
    file_path = tmp_path / "invalid.parquet"
    file_path.write_text("This is not a Parquet file")

    with pytest.raises(ValueError, match="Error reading Parquet file"):
        ParquetHandler.load(file_path)


@pytest.mark.fast
def test_load_missing_pyarrow_dependency(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError when pyarrow is not available."""
    file_path = tmp_path / "test.parquet"
    file_path.touch()  # Create empty file

    with (
        patch("pandas.read_parquet", side_effect=ImportError("No module named 'pyarrow'")),
        pytest.raises(ValueError, match="Error reading Parquet file"),
    ):
        ParquetHandler.load(file_path)


@pytest.mark.fast
def test_load_generic_exception(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for other exceptions."""
    file_path = tmp_path / "test.parquet"
    file_path.touch()  # Create empty file

    with (
        patch("pandas.read_parquet", side_effect=Exception("Generic error")),
        pytest.raises(ValueError, match="Error reading Parquet file"),
    ):
        ParquetHandler.load(file_path)


# Tests for save method
@pytest.mark.fast
def test_save_method_is_static() -> None:
    """Test that the save method is static."""
    assert callable(ParquetHandler.save)


@pytest.mark.fast
def test_save_permission_error(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test that save raises PermissionError for permission issues."""
    # Create a file that we can't write to (simulate permission error)
    file_path = tmp_path / "readonly.parquet"
    file_path.touch()
    file_path.chmod(0o444)  # Read-only

    try:
        with pytest.raises(PermissionError, match="Permission denied when saving Parquet to"):
            ParquetHandler.save(sample_parquet_data, file_path)
    finally:
        # Restore permissions for cleanup
        file_path.chmod(0o666)


@pytest.mark.fast
def test_save_os_error(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test that save raises OSError for OS-level errors."""
    # Create a directory that doesn't exist
    file_path = tmp_path / "nonexistent" / "test.parquet"

    with pytest.raises(OSError, match="OS error while saving Parquet to"):
        ParquetHandler.save(sample_parquet_data, file_path)


@pytest.mark.fast
def test_save_missing_pyarrow_dependency(sample_parquet_data: pd.DataFrame) -> None:
    """Test that save raises OSError when pyarrow is not available."""
    file_path = pathlib.Path("test.parquet")

    with (
        patch("pandas.DataFrame.to_parquet", side_effect=ImportError("No module named 'pyarrow'")),
        pytest.raises(OSError, match="pyarrow library not installed"),
    ):
        ParquetHandler.save(sample_parquet_data, file_path)


# Mock-based tests for successful operations
@pytest.mark.fast
def test_load_successful_with_mock(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test successful loading using mocks."""
    file_path = tmp_path / "test.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=sample_parquet_data):
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, sample_parquet_data)


@pytest.mark.fast
def test_save_successful_with_mock(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test successful saving using mocks."""
    file_path = tmp_path / "test.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(sample_parquet_data, file_path)

    # Verify that to_parquet was called with correct parameters
    mock_to_parquet.assert_called_once()
    call_args = mock_to_parquet.call_args
    assert call_args[1]["index"] is False


@pytest.mark.fast
def test_load_save_roundtrip_with_mock(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test that data can be saved and loaded back correctly using mocks."""
    file_path = tmp_path / "roundtrip.parquet"
    file_path.touch()

    with patch("pandas.DataFrame.to_parquet"), patch("pandas.read_parquet", return_value=sample_parquet_data):
        # Save the DataFrame
        ParquetHandler.save(sample_parquet_data, file_path)

        # Load it back
        loaded_df = ParquetHandler.load(file_path)

        # Verify the data is the same
        pd.testing.assert_frame_equal(loaded_df, sample_parquet_data)


# Tests for different file extensions
@pytest.mark.parametrize("file_extension", [".parquet", ".pq"])
@pytest.mark.fast
def test_load_successful_parquet_file_extensions(file_extension: str, tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test successful loading of Parquet files with different extensions."""
    file_path = tmp_path / f"test{file_extension}"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=sample_parquet_data):
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, sample_parquet_data)


@pytest.mark.parametrize("file_extension", [".parquet", ".pq"])
@pytest.mark.fast
def test_save_successful_parquet_file_extensions(file_extension: str, tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test successful saving of Parquet files with different extensions."""
    file_path = tmp_path / f"test{file_extension}"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(sample_parquet_data, file_path)

    # Verify that to_parquet was called with correct parameters
    mock_to_parquet.assert_called_once()
    call_args = mock_to_parquet.call_args
    assert call_args[1]["index"] is False


# Tests for edge cases
@pytest.mark.fast
def test_save_empty_dataframe_with_mock(tmp_path: pathlib.Path) -> None:
    """Test saving an empty DataFrame using mocks."""
    empty_df = pd.DataFrame()
    file_path = tmp_path / "empty.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(empty_df, file_path)

    # Verify that to_parquet was called
    mock_to_parquet.assert_called_once()


@pytest.mark.fast
def test_load_empty_parquet_file_with_mock(tmp_path: pathlib.Path) -> None:
    """Test loading an empty Parquet file using mocks."""
    empty_df = pd.DataFrame()
    file_path = tmp_path / "empty.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=empty_df):
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


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

    file_path = tmp_path / "mixed_types.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(mixed_df, file_path)

    # Verify that to_parquet was called
    mock_to_parquet.assert_called_once()


@pytest.mark.fast
def test_load_dataframe_with_different_data_types(tmp_path: pathlib.Path) -> None:
    """Test loading DataFrame with various data types."""
    mixed_df = pd.DataFrame(
        {
            "string_col": ["text1", "text2", "text3"],
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "bool_col": [True, False, True],
            "null_col": [None, None, None],
        },
    )

    file_path = tmp_path / "mixed_types.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=mixed_df):
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, mixed_df)


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

    file_path = tmp_path / "large.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(large_df, file_path)

    # Verify that to_parquet was called
    mock_to_parquet.assert_called_once()


@pytest.mark.fast
def test_load_large_dataframe(tmp_path: pathlib.Path) -> None:
    """Test loading a large DataFrame."""
    # Create a larger DataFrame
    large_df = pd.DataFrame(
        {
            "col1": range(100),
            "col2": [f"text_{i}" for i in range(100)],
            "col3": [i * 1.5 for i in range(100)],
        },
    )

    file_path = tmp_path / "large.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=large_df):
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, large_df)


@pytest.mark.fast
def test_save_with_datetime_columns(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with datetime columns."""
    datetime_df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3),
            "datetime": pd.date_range("2024-01-01 10:30:00", periods=3, freq="D"),
            "value": [1, 2, 3],
        },
    )

    file_path = tmp_path / "datetime.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(datetime_df, file_path)

    # Verify that to_parquet was called
    mock_to_parquet.assert_called_once()


@pytest.mark.fast
def test_load_with_datetime_columns(tmp_path: pathlib.Path) -> None:
    """Test loading DataFrame with datetime columns."""
    datetime_df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3),
            "datetime": pd.date_range("2024-01-01 10:30:00", periods=3, freq="D"),
            "value": [1, 2, 3],
        },
    )

    file_path = tmp_path / "datetime.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=datetime_df):
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, datetime_df)


# Integration tests
@pytest.mark.fast
def test_load_save_roundtrip(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test that data can be saved and loaded back correctly."""
    file_path = tmp_path / "roundtrip.parquet"

    with patch("pandas.DataFrame.to_parquet"), patch("pandas.read_parquet", return_value=sample_parquet_data):
        # Save the DataFrame
        ParquetHandler.save(sample_parquet_data, file_path)

        # Load it back
        loaded_df = ParquetHandler.load(file_path)

        # Verify the data is the same
        pd.testing.assert_frame_equal(loaded_df, sample_parquet_data)


@pytest.mark.fast
def test_load_save_with_sample_df_fixture(tmp_path: pathlib.Path, sample_df: pd.DataFrame) -> None:
    """Test load/save with the sample_df fixture from conftest."""
    file_path = tmp_path / "sample_df.parquet"

    with patch("pandas.DataFrame.to_parquet"), patch("pandas.read_parquet", return_value=sample_df):
        # Save the DataFrame
        ParquetHandler.save(sample_df, file_path)

        # Load it back
        loaded_df = ParquetHandler.load(file_path)

        # Verify the data is the same
        pd.testing.assert_frame_equal(loaded_df, sample_df)


@pytest.mark.fast
def test_load_save_with_sample_logbook_df_fixture(tmp_path: pathlib.Path, sample_logbook_df: pd.DataFrame) -> None:
    """Test load/save with the sample_logbook_df fixture from conftest."""
    file_path = tmp_path / "sample_logbook_df.parquet"

    with patch("pandas.DataFrame.to_parquet"), patch("pandas.read_parquet", return_value=sample_logbook_df):
        # Save the DataFrame
        ParquetHandler.save(sample_logbook_df, file_path)

        # Load it back
        loaded_df = ParquetHandler.load(file_path)

        # Verify the data is the same
        pd.testing.assert_frame_equal(loaded_df, sample_logbook_df)


# Edge case tests
@pytest.mark.fast
def test_save_to_existing_file_overwrites(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test that saving to an existing file overwrites it."""
    file_path = tmp_path / "overwrite.parquet"

    with patch("pandas.DataFrame.to_parquet"), patch("pandas.read_parquet", return_value=sample_parquet_data):
        # Create initial content
        initial_df = pd.DataFrame({"col1": [1, 2, 3]})
        ParquetHandler.save(initial_df, file_path)

        # Save new content
        ParquetHandler.save(sample_parquet_data, file_path)

        # Verify the new content is there
        loaded_df = ParquetHandler.load(file_path)
        pd.testing.assert_frame_equal(loaded_df, sample_parquet_data)


@pytest.mark.fast
def test_save_with_special_characters_in_filename(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test saving with special characters in filename."""
    file_path = tmp_path / "file with spaces and (parentheses).parquet"

    with patch("pandas.DataFrame.to_parquet"), patch("pandas.read_parquet", return_value=sample_parquet_data):
        # Save the DataFrame
        ParquetHandler.save(sample_parquet_data, file_path)

        # Verify the content by loading it back
        loaded_df = ParquetHandler.load(file_path)
        pd.testing.assert_frame_equal(loaded_df, sample_parquet_data)


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

    file_path = tmp_path / "nested.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(nested_df, file_path)

    # Verify that to_parquet was called
    mock_to_parquet.assert_called_once()


# Tests for method signatures
@pytest.mark.fast
def test_handler_method_signatures() -> None:
    """Test that handler methods have correct signatures."""
    # Check load method signature
    load_sig = inspect.signature(ParquetHandler.load)
    assert "file_path" in load_sig.parameters

    # Check save method signature
    save_sig = inspect.signature(ParquetHandler.save)
    assert "df" in save_sig.parameters
    assert "file_path" in save_sig.parameters


# Tests for error message content
@pytest.mark.fast
def test_load_error_message_content(tmp_path: pathlib.Path) -> None:
    """Test that error messages contain expected content."""
    file_path = tmp_path / "test.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", side_effect=ImportError("No module named 'pyarrow'")):
        with pytest.raises(ValueError, match="Error reading Parquet file") as exc_info:
            ParquetHandler.load(file_path)

        error_message = str(exc_info.value)
        assert "Error reading Parquet file" in error_message
        assert "test.parquet" in error_message


@pytest.mark.fast
def test_save_error_message_content(sample_parquet_data: pd.DataFrame) -> None:
    """Test that save error messages contain expected content."""
    file_path = pathlib.Path("test.parquet")

    with patch("pandas.DataFrame.to_parquet", side_effect=ImportError("No module named 'pyarrow'")):
        with pytest.raises(OSError, match="pyarrow library not installed") as exc_info:
            ParquetHandler.save(sample_parquet_data, file_path)

        error_message = str(exc_info.value)
        assert "pyarrow library not installed" in error_message
        assert "pip install pyarrow" in error_message


@pytest.mark.fast
def test_load_file_not_found_error_message() -> None:
    """Test that FileNotFoundError message contains expected content."""
    file_path = pathlib.Path("nonexistent_file.parquet")

    with pytest.raises(FileNotFoundError, match="Parquet file not found") as exc_info:
        ParquetHandler.load(file_path)

    error_message = str(exc_info.value)
    assert "Parquet file not found" in error_message
    assert "nonexistent_file.parquet" in error_message


@pytest.mark.fast
def test_save_permission_error_message(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test that PermissionError message contains expected content."""
    file_path = tmp_path / "readonly.parquet"
    file_path.touch()
    file_path.chmod(0o444)  # Read-only

    try:
        with pytest.raises(PermissionError, match="Permission denied when saving Parquet to") as exc_info:
            ParquetHandler.save(sample_parquet_data, file_path)

        error_message = str(exc_info.value)
        assert "Permission denied when saving Parquet to" in error_message
        assert "readonly.parquet" in error_message
    finally:
        # Restore permissions for cleanup
        file_path.chmod(0o666)


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

    file_path = tmp_path / "performance.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        start_time = time.time()
        ParquetHandler.save(df, file_path)
        end_time = time.time()

    # Should complete in less than 5 seconds
    assert end_time - start_time < 5.0
    mock_to_parquet.assert_called_once()


@pytest.mark.fast
def test_load_performance(tmp_path: pathlib.Path) -> None:
    """Test that load is reasonably fast."""
    # Create a moderately sized DataFrame
    df = pd.DataFrame(
        {
            "col1": range(100),
            "col2": [f"text_{i}" for i in range(100)],
            "col3": [i * 1.5 for i in range(100)],
        },
    )

    file_path = tmp_path / "performance.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=df):
        start_time = time.time()
        ParquetHandler.load(file_path)
        end_time = time.time()

    # Should complete in less than 5 seconds
    assert end_time - start_time < 5.0


# Tests for Parquet-specific features
@pytest.mark.fast
def test_save_with_compression(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test saving with compression (mocked)."""
    file_path = tmp_path / "compressed.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(sample_parquet_data, file_path)

    # Verify that to_parquet was called with correct parameters
    mock_to_parquet.assert_called_once()
    call_args = mock_to_parquet.call_args
    assert call_args[1]["index"] is False


@pytest.mark.fast
def test_load_with_different_engines(tmp_path: pathlib.Path, sample_parquet_data: pd.DataFrame) -> None:
    """Test loading with different engines (mocked)."""
    file_path = tmp_path / "test.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=sample_parquet_data) as mock_read_parquet:
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, sample_parquet_data)
    mock_read_parquet.assert_called_once()


# Tests for data type preservation
@pytest.mark.fast
def test_data_type_preservation(tmp_path: pathlib.Path) -> None:
    """Test that data types are preserved through save/load cycle."""
    # Create DataFrame with specific data types
    original_df = pd.DataFrame(
        {
            "int_col": pd.Series([1, 2, 3], dtype="int32"),
            "float_col": pd.Series([1.1, 2.2, 3.3], dtype="float64"),
            "string_col": pd.Series(["a", "b", "c"], dtype="string"),
            "bool_col": pd.Series([True, False, True], dtype="bool"),
            "category_col": pd.Series(["A", "B", "A"], dtype="category"),
        },
    )

    file_path = tmp_path / "data_types.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=original_df), patch("pandas.DataFrame.to_parquet"):
        # Save and load
        ParquetHandler.save(original_df, file_path)
        loaded_df = ParquetHandler.load(file_path)

        # Verify data types are preserved
        pd.testing.assert_frame_equal(loaded_df, original_df)


# Tests for handling of NaN values
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

    file_path = tmp_path / "nan_values.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(nan_df, file_path)

    # Verify that to_parquet was called
    mock_to_parquet.assert_called_once()


@pytest.mark.fast
def test_load_with_nan_values(tmp_path: pathlib.Path) -> None:
    """Test loading DataFrame with NaN values."""
    nan_df = pd.DataFrame(
        {
            "col1": [1, 2, float("nan"), 4, 5],
            "col2": ["a", "b", None, "d", "e"],
            "col3": [1.1, 2.2, float("nan"), 4.4, 5.5],
        },
    )

    file_path = tmp_path / "nan_values.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=nan_df):
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, nan_df)


# Tests for handling of Unicode characters
@pytest.mark.fast
def test_save_with_unicode_characters(tmp_path: pathlib.Path) -> None:
    """Test saving DataFrame with unicode characters."""
    unicode_df = pd.DataFrame(
        {
            "text": ["café", "naïve", "façade", "résumé", "über"],
            "numbers": [1, 2, 3, 4, 5],
        },
    )

    file_path = tmp_path / "unicode.parquet"

    with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
        ParquetHandler.save(unicode_df, file_path)

    # Verify that to_parquet was called
    mock_to_parquet.assert_called_once()


@pytest.mark.fast
def test_load_with_unicode_characters(tmp_path: pathlib.Path) -> None:
    """Test loading DataFrame with unicode characters."""
    unicode_df = pd.DataFrame(
        {
            "text": ["café", "naïve", "façade", "résumé", "über"],
            "numbers": [1, 2, 3, 4, 5],
        },
    )

    file_path = tmp_path / "unicode.parquet"
    file_path.touch()

    with patch("pandas.read_parquet", return_value=unicode_df):
        result = ParquetHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, unicode_df)

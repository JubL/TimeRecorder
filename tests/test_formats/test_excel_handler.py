"""Tests for the ExcelHandler class in src.formats.excel_handler."""

import inspect
import pathlib
from unittest.mock import patch

import pandas as pd
import pytest

from src.formats.base import BaseFormatHandler
from src.formats.excel_handler import ExcelHandler


@pytest.fixture
def excel_handler() -> ExcelHandler:
    """Fixture to create an ExcelHandler instance."""
    return ExcelHandler()


@pytest.fixture
def sample_excel_data() -> pd.DataFrame:
    """Fixture to create sample data for Excel testing."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "salary": [50000.0, 60000.0, 70000.0, 55000.0, 65000.0],
            "department": ["HR", "IT", "Sales", "Marketing", "Finance"],
        },
    )


# Tests for ExcelHandler class
@pytest.mark.fast
def test_excel_handler_instantiation() -> None:
    """Test that ExcelHandler can be instantiated."""
    handler = ExcelHandler()
    assert isinstance(handler, ExcelHandler)


@pytest.mark.fast
def test_excel_handler_inherits_from_base() -> None:
    """Test that ExcelHandler inherits from BaseFormatHandler."""
    handler = ExcelHandler()
    assert isinstance(handler, BaseFormatHandler)


@pytest.mark.fast
def test_excel_handler_has_required_methods() -> None:
    """Test that ExcelHandler has the required methods."""
    handler = ExcelHandler()

    assert hasattr(handler, "load")
    assert hasattr(handler, "save")
    assert callable(handler.load)
    assert callable(handler.save)


# Tests for load method
@pytest.mark.fast
def test_load_method_is_static() -> None:
    """Test that the load method is static."""
    assert callable(ExcelHandler.load)


@pytest.mark.fast
def test_load_file_not_found() -> None:
    """Test that load raises FileNotFoundError for non-existent files."""
    file_path = pathlib.Path("nonexistent_file.xlsx")

    with pytest.raises(FileNotFoundError, match="Excel file not found"):
        ExcelHandler.load(file_path)


@pytest.mark.fast
def test_load_invalid_excel_format(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for invalid Excel format."""
    # Create a file that's not a valid Excel file
    file_path = tmp_path / "invalid.xlsx"
    file_path.write_text("This is not an Excel file")

    with pytest.raises(ValueError, match="Invalid Excel format"):
        ExcelHandler.load(file_path)


@pytest.mark.fast
def test_load_missing_openpyxl_dependency(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError when openpyxl is not available."""
    file_path = tmp_path / "test.xlsx"
    file_path.touch()  # Create empty file

    with (
        patch("pandas.read_excel", side_effect=ImportError("No module named 'openpyxl'")),
        pytest.raises(ValueError, match="openpyxl library not installed"),
    ):
        ExcelHandler.load(file_path)


@pytest.mark.fast
def test_load_generic_exception(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for other exceptions."""
    file_path = tmp_path / "test.xlsx"
    file_path.touch()  # Create empty file

    with (
        patch("pandas.read_excel", side_effect=Exception("Generic error")),
        pytest.raises(ValueError, match="Invalid Excel format"),
    ):
        ExcelHandler.load(file_path)


# Tests for save method
@pytest.mark.fast
def test_save_method_is_static() -> None:
    """Test that the save method is static."""
    assert callable(ExcelHandler.save)


@pytest.mark.fast
def test_save_permission_error(tmp_path: pathlib.Path, sample_excel_data: pd.DataFrame) -> None:
    """Test that save raises PermissionError for permission issues."""
    # Create a file that we can't write to (simulate permission error)
    file_path = tmp_path / "readonly.xlsx"
    file_path.touch()
    file_path.chmod(0o444)  # Read-only

    try:
        with pytest.raises(PermissionError, match="Permission denied"):
            ExcelHandler.save(sample_excel_data, file_path)
    finally:
        # Restore permissions for cleanup
        file_path.chmod(0o666)


@pytest.mark.fast
def test_save_os_error(tmp_path: pathlib.Path, sample_excel_data: pd.DataFrame) -> None:
    """Test that save raises OSError for OS-level errors."""
    # Create a directory that doesn't exist
    file_path = tmp_path / "nonexistent" / "test.xlsx"

    with pytest.raises(OSError, match="OS error"):
        ExcelHandler.save(sample_excel_data, file_path)


@pytest.mark.fast
def test_save_missing_openpyxl_dependency(sample_excel_data: pd.DataFrame) -> None:
    """Test that save raises OSError when openpyxl is not available."""
    file_path = pathlib.Path("test.xlsx")

    with (
        patch("pandas.DataFrame.to_excel", side_effect=ImportError("No module named 'openpyxl'")),
        pytest.raises(OSError, match="openpyxl library not installed"),
    ):
        ExcelHandler.save(sample_excel_data, file_path)


# Mock-based tests for successful operations
@pytest.mark.fast
def test_load_successful_with_mock(tmp_path: pathlib.Path, sample_excel_data: pd.DataFrame) -> None:
    """Test successful loading using mocks."""
    file_path = tmp_path / "test.xlsx"
    file_path.touch()

    with patch("pandas.read_excel", return_value=sample_excel_data):
        result = ExcelHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, sample_excel_data)


@pytest.mark.fast
def test_save_successful_with_mock(tmp_path: pathlib.Path, sample_excel_data: pd.DataFrame) -> None:
    """Test successful saving using mocks."""
    file_path = tmp_path / "test.xlsx"

    with patch("pandas.DataFrame.to_excel") as mock_to_excel:
        ExcelHandler.save(sample_excel_data, file_path)

    # Verify that to_excel was called with correct parameters
    mock_to_excel.assert_called_once()
    call_args = mock_to_excel.call_args
    assert call_args[1]["index"] is False
    assert call_args[1]["engine"] == "openpyxl"


@pytest.mark.fast
def test_load_save_roundtrip_with_mock(tmp_path: pathlib.Path, sample_excel_data: pd.DataFrame) -> None:
    """Test that data can be saved and loaded back correctly using mocks."""
    file_path = tmp_path / "roundtrip.xlsx"
    file_path.touch()

    with patch("pandas.DataFrame.to_excel"), patch("pandas.read_excel", return_value=sample_excel_data):
        # Save the DataFrame
        ExcelHandler.save(sample_excel_data, file_path)

        # Load it back
        loaded_df = ExcelHandler.load(file_path)

        # Verify the data is the same
        pd.testing.assert_frame_equal(loaded_df, sample_excel_data)


# Tests for different file extensions
@pytest.mark.parametrize(
    "file_extension",
    [".xlsx", ".xls"],
)
@pytest.mark.fast
def test_load_successful_excel_file_extensions(file_extension: str, tmp_path: pathlib.Path, sample_excel_data: pd.DataFrame) -> None:
    """Test successful loading of Excel files with different extensions."""
    file_path = tmp_path / f"test{file_extension}"
    file_path.touch()

    with patch("pandas.read_excel", return_value=sample_excel_data):
        result = ExcelHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, sample_excel_data)


@pytest.mark.parametrize(
    "file_extension",
    [".xlsx", ".xls"],
)
@pytest.mark.fast
def test_save_successful_excel_file_extensions(file_extension: str, tmp_path: pathlib.Path, sample_excel_data: pd.DataFrame) -> None:
    """Test successful saving of Excel files with different extensions."""
    file_path = tmp_path / f"test{file_extension}"

    with patch("pandas.DataFrame.to_excel") as mock_to_excel:
        ExcelHandler.save(sample_excel_data, file_path)

    # Verify that to_excel was called with correct parameters
    mock_to_excel.assert_called_once()
    call_args = mock_to_excel.call_args
    assert call_args[1]["index"] is False
    assert call_args[1]["engine"] == "openpyxl"


# Tests for edge cases
@pytest.mark.fast
def test_save_empty_dataframe_with_mock(tmp_path: pathlib.Path) -> None:
    """Test saving an empty DataFrame using mocks."""
    empty_df = pd.DataFrame()
    file_path = tmp_path / "empty.xlsx"

    with patch("pandas.DataFrame.to_excel") as mock_to_excel:
        ExcelHandler.save(empty_df, file_path)

    # Verify that to_excel was called
    mock_to_excel.assert_called_once()


@pytest.mark.fast
def test_load_empty_excel_file_with_mock(tmp_path: pathlib.Path) -> None:
    """Test loading an empty Excel file using mocks."""
    empty_df = pd.DataFrame()
    file_path = tmp_path / "empty.xlsx"
    file_path.touch()

    with patch("pandas.read_excel", return_value=empty_df):
        result = ExcelHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


# Tests for method signatures
@pytest.mark.fast
def test_handler_method_signatures() -> None:
    """Test that handler methods have correct signatures."""
    # Check load method signature
    load_sig = inspect.signature(ExcelHandler.load)
    assert "file_path" in load_sig.parameters

    # Check save method signature
    save_sig = inspect.signature(ExcelHandler.save)
    assert "df" in save_sig.parameters
    assert "file_path" in save_sig.parameters


# Tests for error message content
@pytest.mark.fast
def test_load_error_message_content(tmp_path: pathlib.Path) -> None:
    """Test that error messages contain expected content."""
    file_path = tmp_path / "test.xlsx"
    file_path.touch()

    with patch("pandas.read_excel", side_effect=ImportError("No module named 'openpyxl'")):
        with pytest.raises(ValueError, match="openpyxl library not installed") as exc_info:
            ExcelHandler.load(file_path)

        error_message = str(exc_info.value)
        assert "openpyxl library not installed" in error_message
        assert "pip install openpyxl" in error_message


@pytest.mark.fast
def test_save_error_message_content(sample_excel_data: pd.DataFrame) -> None:
    """Test that save error messages contain expected content."""
    file_path = pathlib.Path("test.xlsx")

    with patch("pandas.DataFrame.to_excel", side_effect=ImportError("No module named 'openpyxl'")):
        with pytest.raises(OSError, match="openpyxl library not installed") as exc_info:
            ExcelHandler.save(sample_excel_data, file_path)

        error_message = str(exc_info.value)
        assert "openpyxl library not installed" in error_message
        assert "pip install openpyxl" in error_message

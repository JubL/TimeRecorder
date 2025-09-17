"""Tests for the XMLHandler class in src.formats.xml_handler."""

import pathlib

import pandas as pd
import pytest

from src.formats.base import BaseFormatHandler
from src.formats.xml_handler import XMLHandler


@pytest.fixture
def xml_handler() -> XMLHandler:
    """Fixture to create a XMLHandler instance."""
    return XMLHandler()


@pytest.fixture
def sample_xml_data() -> pd.DataFrame:
    """Fixture to create sample data for XML testing."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "department": ["HR", "IT", "Sales"],
        },
    )


# Basic tests
@pytest.mark.fast
def test_xml_handler_instantiation() -> None:
    """Test that XMLHandler can be instantiated."""
    handler = XMLHandler()
    assert isinstance(handler, XMLHandler)


@pytest.mark.fast
def test_xml_handler_inherits_from_base() -> None:
    """Test that XMLHandler inherits from BaseFormatHandler."""
    handler = XMLHandler()
    assert isinstance(handler, BaseFormatHandler)


@pytest.mark.fast
def test_xml_handler_has_required_methods() -> None:
    """Test that XMLHandler has the required methods."""
    handler = XMLHandler()
    assert hasattr(handler, "load")
    assert hasattr(handler, "save")
    assert callable(handler.load)
    assert callable(handler.save)


# Load method tests
@pytest.mark.fast
def test_load_method_is_static() -> None:
    """Test that the load method is static."""
    assert callable(XMLHandler.load)


@pytest.mark.fast
def test_load_successful_xml_file(tmp_path: pathlib.Path, sample_xml_data: pd.DataFrame) -> None:
    """Test successful loading of XML file."""
    file_path = tmp_path / "test.xml"

    # Create XML file using pandas
    sample_xml_data.to_xml(file_path, index=False, root_name="logbook", row_name="record")

    # Load the file
    result = XMLHandler.load(file_path)

    # Verify the result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_xml_data)
    assert list(result.columns) == ["name", "age", "department"]
    assert result["age"].dtype == "int64"


@pytest.mark.fast
def test_load_empty_xml_file(tmp_path: pathlib.Path) -> None:
    """Test loading XML file with empty data."""
    file_path = tmp_path / "empty.xml"

    # Create empty XML file
    empty_df = pd.DataFrame()
    empty_df.to_xml(file_path, index=False, root_name="logbook", row_name="record")

    # Load the file
    with pytest.raises(ValueError, match="Invalid XML format"):
        XMLHandler.load(file_path)


@pytest.mark.fast
def test_load_file_not_found() -> None:
    """Test that load raises FileNotFoundError for non-existent files."""
    file_path = pathlib.Path("nonexistent_file.xml")

    with pytest.raises(FileNotFoundError, match="XML file not found"):
        XMLHandler.load(file_path)


@pytest.mark.fast
def test_load_invalid_xml_format(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for invalid XML format."""
    file_path = tmp_path / "invalid.xml"
    file_path.write_text("This is not valid XML")

    with pytest.raises(ValueError, match="Invalid XML format"):
        XMLHandler.load(file_path)


# Save method tests
@pytest.mark.fast
def test_save_method_is_static() -> None:
    """Test that the save method is static."""
    assert callable(XMLHandler.save)


@pytest.mark.fast
def test_save_successful_xml_file(tmp_path: pathlib.Path, sample_xml_data: pd.DataFrame) -> None:
    """Test successful saving of XML files."""
    file_path = tmp_path / "test.xml"

    # Save the DataFrame
    XMLHandler.save(sample_xml_data, file_path)

    # Verify the file was created
    assert file_path.exists()
    assert file_path.stat().st_size > 0

    # Verify the content by loading it back
    loaded_df = pd.read_xml(file_path)
    pd.testing.assert_frame_equal(loaded_df, sample_xml_data, check_dtype=False)


@pytest.mark.fast
def test_save_empty_dataframe(tmp_path: pathlib.Path) -> None:
    """Test saving an empty DataFrame."""
    empty_df = pd.DataFrame()
    file_path = tmp_path / "empty.xml"

    # Save the empty DataFrame
    XMLHandler.save(empty_df, file_path)

    # Verify the file was created
    assert file_path.exists()


@pytest.mark.fast
def test_save_permission_error(tmp_path: pathlib.Path, sample_xml_data: pd.DataFrame) -> None:
    """Test that save raises PermissionError for permission issues."""
    file_path = tmp_path / "readonly.xml"
    file_path.touch()
    file_path.chmod(0o444)  # Read-only

    try:
        with pytest.raises(PermissionError, match="Permission denied"):
            XMLHandler.save(sample_xml_data, file_path)
    finally:
        # Restore permissions for cleanup
        file_path.chmod(0o666)


@pytest.mark.fast
def test_save_os_error(tmp_path: pathlib.Path, sample_xml_data: pd.DataFrame) -> None:
    """Test that save raises OSError for OS-level errors."""
    file_path = tmp_path / "nonexistent" / "test.xml"

    with pytest.raises(OSError, match="OS error"):
        XMLHandler.save(sample_xml_data, file_path)


# Integration tests
@pytest.mark.fast
def test_load_save_roundtrip(tmp_path: pathlib.Path, sample_xml_data: pd.DataFrame) -> None:
    """Test that data can be saved and loaded back correctly."""
    file_path = tmp_path / "roundtrip.xml"

    # Save the DataFrame
    XMLHandler.save(sample_xml_data, file_path)

    # Load it back
    loaded_df = XMLHandler.load(file_path)

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_xml_data, check_dtype=False)


@pytest.mark.fast
def test_load_save_with_sample_df_fixture(tmp_path: pathlib.Path, sample_df: pd.DataFrame) -> None:
    """Test load/save with the sample_df fixture from conftest."""
    file_path = tmp_path / "sample_df.xml"

    # Save the DataFrame
    XMLHandler.save(sample_df, file_path)

    # Load it back
    loaded_df = XMLHandler.load(file_path)

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_df, check_dtype=False)


@pytest.mark.fast
def test_load_save_with_sample_logbook_df_fixture(tmp_path: pathlib.Path, sample_logbook_df: pd.DataFrame) -> None:
    """Test load/save with the sample_logbook_df fixture from conftest."""
    file_path = tmp_path / "sample_logbook_df.xml"

    # Save the DataFrame
    XMLHandler.save(sample_logbook_df, file_path)

    # Load it back
    loaded_df = XMLHandler.load(file_path)

    print(loaded_df.iloc[:, 4])
    print(sample_logbook_df.iloc[:, 4])

    # Verify the data is the same
    pd.testing.assert_frame_equal(loaded_df, sample_logbook_df, check_dtype=False)

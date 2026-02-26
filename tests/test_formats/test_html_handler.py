"""Tests for the HTMLHandler class in src.formats.html_handler."""

import pathlib

import pandas as pd
import pytest

from src.formats.base import BaseFormatHandler
from src.formats.html_handler import HTMLHandler


@pytest.fixture
def html_handler() -> HTMLHandler:
    """Fixture to create an HTMLHandler instance."""
    return HTMLHandler()


@pytest.fixture
def sample_html_data() -> pd.DataFrame:
    """Fixture to create sample data for HTML testing."""
    return pd.DataFrame(
        {
            "weekday": ["Mon", "Tue", "Wed"],
            "date": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "start_time": ["08:00:00", "07:30:00", "08:15:00"],
            "end_time": ["17:00:00", "16:30:00", "17:15:00"],
            "work_time": [8.0, 7.5, 8.25],
            "overtime": [0.0, -0.5, 0.25],
        },
    )


# Tests for HTMLHandler class
@pytest.mark.fast
def test_html_handler_instantiation() -> None:
    """Test that HTMLHandler can be instantiated."""
    handler = HTMLHandler()
    assert isinstance(handler, HTMLHandler)


@pytest.mark.fast
def test_html_handler_inherits_from_base() -> None:
    """Test that HTMLHandler inherits from BaseFormatHandler."""
    handler = HTMLHandler()
    assert isinstance(handler, BaseFormatHandler)


@pytest.mark.fast
def test_html_handler_has_required_methods() -> None:
    """Test that HTMLHandler has the required methods."""
    handler = HTMLHandler()

    assert hasattr(handler, "load")
    assert hasattr(handler, "save")
    assert callable(handler.load)
    assert callable(handler.save)


# Tests for load method
@pytest.mark.fast
def test_load_successful(tmp_path: pathlib.Path, sample_html_data: pd.DataFrame) -> None:
    """Test successful loading of HTML file."""
    file_path = tmp_path / "test.html"

    HTMLHandler.save(sample_html_data, file_path)
    result = HTMLHandler.load(file_path)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_html_data)
    assert list(result.columns) == list(sample_html_data.columns)
    pd.testing.assert_frame_equal(result, sample_html_data, check_dtype=False)


@pytest.mark.fast
def test_load_file_not_found() -> None:
    """Test that load raises FileNotFoundError for non-existent file."""
    file_path = pathlib.Path("nonexistent.html")

    with pytest.raises(FileNotFoundError, match="HTML file not found"):
        HTMLHandler.load(file_path)


@pytest.mark.fast
def test_load_empty_file(tmp_path: pathlib.Path) -> None:
    """Test that load raises ValueError for HTML file with no tables."""
    file_path = tmp_path / "empty.html"
    file_path.write_text("<html><body><p>No table here</p></body></html>", encoding="utf-8")

    with pytest.raises(ValueError, match=r"No tables found|No HTML tables found"):
        HTMLHandler.load(file_path)


# Tests for save method
@pytest.mark.fast
def test_save_creates_file(tmp_path: pathlib.Path, sample_html_data: pd.DataFrame) -> None:
    """Test that save creates an HTML file."""
    file_path = tmp_path / "output.html"

    HTMLHandler.save(sample_html_data, file_path)

    assert file_path.exists()
    content = file_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "<table" in content
    assert "TimeRecorder Logbook" in content


@pytest.mark.fast
def test_save_empty_dataframe(tmp_path: pathlib.Path) -> None:
    """Test saving an empty DataFrame."""
    file_path = tmp_path / "empty.html"
    empty_df = pd.DataFrame(columns=["weekday", "date", "work_time"])

    HTMLHandler.save(empty_df, file_path)

    assert file_path.exists()
    loaded = HTMLHandler.load(file_path)
    assert len(loaded) == 0
    assert list(loaded.columns) == ["weekday", "date", "work_time"]


# Round-trip tests
@pytest.mark.fast
def test_load_save_roundtrip(tmp_path: pathlib.Path, sample_html_data: pd.DataFrame) -> None:
    """Test that data can be saved and loaded back correctly."""
    file_path = tmp_path / "roundtrip.html"

    HTMLHandler.save(sample_html_data, file_path)
    loaded_df = HTMLHandler.load(file_path)

    pd.testing.assert_frame_equal(loaded_df, sample_html_data, check_dtype=False)


@pytest.mark.fast
def test_load_save_with_sample_logbook_df_fixture(
    tmp_path: pathlib.Path,
    sample_logbook_df: pd.DataFrame,
) -> None:
    """Test load/save with the sample_logbook_df fixture from conftest."""
    file_path = tmp_path / "sample_logbook_df.html"

    HTMLHandler.save(sample_logbook_df, file_path)
    loaded_df = HTMLHandler.load(file_path)

    pd.testing.assert_frame_equal(loaded_df, sample_logbook_df, check_dtype=False)

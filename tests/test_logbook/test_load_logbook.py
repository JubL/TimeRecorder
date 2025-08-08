from unittest.mock import patch

import pandas as pd
import pytest

import src.logbook as lb


@pytest.mark.fast
def test_load_logbook_file_not_found_error_with_mock_read_csv(logbook: lb.Logbook) -> None:
    """Test that load_logbook handles FileNotFoundError gracefully by mocking pd.read_csv."""
    # Create a valid file so the initial check passes
    logbook.create_df()

    # Mock pd.read_csv to raise FileNotFoundError
    with patch("pandas.read_csv", side_effect=FileNotFoundError("File not found")), pytest.raises(FileNotFoundError):
        logbook.load_logbook()


@pytest.mark.fast
def test_load_logbook_empty_data_error_with_mock_read_csv(logbook: lb.Logbook) -> None:
    """Test that load_logbook handles EmptyDataError gracefully by mocking pd.read_csv."""
    # Create a valid file so the initial check passes
    logbook.create_df()

    # Mock pd.read_csv to raise EmptyDataError
    with patch("pandas.read_csv", side_effect=pd.errors.EmptyDataError("No data")), pytest.raises(pd.errors.EmptyDataError):
        logbook.load_logbook()


@pytest.mark.fast
def test_load_logbook_parser_error_with_mock_read_csv(logbook: lb.Logbook) -> None:
    """Test that load_logbook handles ParserError gracefully by mocking pd.read_csv."""
    # Create a valid file so the initial check passes
    logbook.create_df()

    # Mock pd.read_csv to raise ParserError
    with patch("pandas.read_csv", side_effect=pd.errors.ParserError("Parse error")), pytest.raises(pd.errors.ParserError):
        logbook.load_logbook()


@pytest.mark.fast
def test_load_logbook_missing_required_columns(logbook: lb.Logbook) -> None:
    """Test that load_logbook raises KeyError when required columns are missing."""
    # Create a CSV file with missing columns
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": ["01.01.2024"],
            "start_time": ["09:00"],
            # Missing: end_time, lunch_break_duration, work_time, case, overtime
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    with pytest.raises(KeyError) as exc_info:
        logbook.load_logbook()

    assert "Log file is missing required columns" in str(exc_info.value)


@pytest.mark.fast
def test_load_logbook_unexpected_number_of_columns(logbook: lb.Logbook) -> None:
    """Test that load_logbook raises ValueError when there are unexpected number of columns."""
    # Create a CSV file with extra columns
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": ["01.01.2024"],
            "start_time": ["09:00"],
            "end_time": ["17:00"],
            "lunch_break_duration": ["1.0"],
            "work_time": ["8.0"],
            "case": ["normal"],
            "overtime": ["0.0"],
            "extra_column": ["extra_value"],  # Extra column
        },
    )
    df.to_csv(logbook.get_path(), sep=";", index=False)

    with pytest.raises(ValueError, match="Log file has an unexpected number of columns") as exc_info:
        logbook.load_logbook()

    assert "Expected 8 columns" in str(exc_info.value)


@pytest.mark.fast
def test_save_logbook_permission_error(logbook: lb.Logbook) -> None:
    """Test that save_logbook raises PermissionError when permission is denied."""
    # Create a test DataFrame
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": ["01.01.2024"],
            "start_time": ["09:00"],
            "end_time": ["17:00"],
            "lunch_break_duration": ["1.0"],
            "work_time": ["8.0"],
            "case": ["normal"],
            "overtime": ["0.0"],
        },
    )

    # Mock pd.DataFrame.to_csv to raise PermissionError
    with patch.object(df, "to_csv", side_effect=PermissionError("Permission denied")):
        with pytest.raises(PermissionError) as exc_info:
            logbook.save_logbook(df)

        # Verify that the exception message is correct
        assert "Permission denied when saving logbook" in str(exc_info.value)


@pytest.mark.fast
def test_save_logbook_os_error(logbook: lb.Logbook) -> None:
    """Test that save_logbook raises OSError when OS error occurs."""
    # Create a test DataFrame
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": ["01.01.2024"],
            "start_time": ["09:00"],
            "end_time": ["17:00"],
            "lunch_break_duration": ["1.0"],
            "work_time": ["8.0"],
            "case": ["normal"],
            "overtime": ["0.0"],
        },
    )

    # Mock pd.DataFrame.to_csv to raise OSError
    with patch.object(df, "to_csv", side_effect=OSError("Disk full")):
        with pytest.raises(OSError, match="OS error while saving logbook") as exc_info:
            logbook.save_logbook(df)

        # Verify that the exception message is correct
        assert "OS error while saving logbook" in str(exc_info.value)


@pytest.mark.fast
def test_save_logbook_with_timestamp_date_column(logbook: lb.Logbook) -> None:
    """Test that save_logbook converts timestamp date column to string format."""
    # Create a test DataFrame with timestamp date column
    df = pd.DataFrame(
        {
            "weekday": ["Mon"],
            "date": [pd.Timestamp("2024-01-01")],
            "start_time": ["09:00"],
            "end_time": ["17:00"],
            "lunch_break_duration": ["1.0"],
            "work_time": ["8.0"],
            "case": ["normal"],
            "overtime": ["0.0"],
        },
    )

    # Mock the to_csv method to avoid actual file writing
    with patch.object(df, "to_csv") as mock_to_csv:
        logbook.save_logbook(df)

        # Verify that to_csv was called
        mock_to_csv.assert_called_once()

        # Verify that the date column was converted to string format
        # The date should be in the format specified by logbook.date_format
        assert isinstance(df["date"].iloc[0], str)


@pytest.mark.fast
def test_load_logbook_invalid_case_values(logbook: lb.Logbook) -> None:
    """Test that load_logbook raises ValueError when invalid case values are found (line 181)."""
    # Create a CSV file with invalid case values
    invalid_df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["24.04.2025", "25.04.2025"],
            "start_time": ["08:00:00", "09:00:00"],
            "end_time": ["17:00:00", "18:00:00"],
            "lunch_break_duration": [30, 45],
            "work_time": [8.5, 8.25],
            "case": ["invalid_case", "overtime"],  # Invalid case value
            "overtime": [0.5, 0.25],
        },
    )

    # Save the invalid DataFrame to the logbook file
    logbook.save_logbook(invalid_df)

    # Test that load_logbook raises ValueError for invalid case values
    with pytest.raises(ValueError, match="Log file has invalid case values"):
        logbook.load_logbook()


@pytest.mark.fast
def test_load_logbook_valid_case_values(logbook: lb.Logbook) -> None:
    """Test that load_logbook works correctly with valid case values and covers the return statement."""
    # Create a CSV file with valid case values
    valid_df = pd.DataFrame(
        {
            "weekday": ["Mon", "Tue"],
            "date": ["24.04.2025", "25.04.2025"],
            "start_time": ["08:00:00", "09:00:00"],
            "end_time": ["17:00:00", "18:00:00"],
            "lunch_break_duration": [30, 45],
            "work_time": [8.5, 8.25],
            "case": ["overtime", "undertime"],  # Valid case values
            "overtime": [0.5, 0.25],
        },
    )

    # Save the valid DataFrame to the logbook file
    logbook.save_logbook(valid_df)

    # Test that load_logbook works correctly with valid case values
    result = logbook.load_logbook()
    assert len(result) == 2
    assert list(result["case"]) == ["overtime", "undertime"]

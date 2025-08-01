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
    with patch("pandas.read_csv", side_effect=FileNotFoundError("File not found")), patch("src.logbook.logger") as mock_logger:
        with pytest.raises(FileNotFoundError) as exc_info:
            logbook.load_logbook()

        # Verify that the exception was logged
        mock_logger.exception.assert_called_once()
        assert "Log file not found" in str(exc_info.value)


@pytest.mark.fast
def test_load_logbook_empty_data_error_with_mock_read_csv(logbook: lb.Logbook) -> None:
    """Test that load_logbook handles EmptyDataError gracefully by mocking pd.read_csv."""
    # Create a valid file so the initial check passes
    logbook.create_df()

    # Mock pd.read_csv to raise EmptyDataError
    with patch("pandas.read_csv", side_effect=pd.errors.EmptyDataError("No data")), patch("src.logbook.logger") as mock_logger:
        with pytest.raises(pd.errors.EmptyDataError) as exc_info:
            logbook.load_logbook()

        # Verify that the exception was logged
        mock_logger.exception.assert_called_once()
        assert "Log file is empty" in str(exc_info.value)


@pytest.mark.fast
def test_load_logbook_parser_error_with_mock_read_csv(logbook: lb.Logbook) -> None:
    """Test that load_logbook handles ParserError gracefully by mocking pd.read_csv."""
    # Create a valid file so the initial check passes
    logbook.create_df()

    # Mock pd.read_csv to raise ParserError
    with patch("pandas.read_csv", side_effect=pd.errors.ParserError("Parse error")), patch("src.logbook.logger") as mock_logger:
        with pytest.raises(pd.errors.ParserError) as exc_info:
            logbook.load_logbook()

        # Verify that the exception was logged
        mock_logger.exception.assert_called_once()
        assert "Error parsing log file" in str(exc_info.value)


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
    """Test that save_logbook handles PermissionError gracefully."""
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
    with patch.object(df, "to_csv", side_effect=PermissionError("Permission denied")), patch("src.logbook.logger") as mock_logger:
        logbook.save_logbook(df)

        # Verify that the exception was logged
        mock_logger.exception.assert_called_once()
        assert "Permission denied when saving logbook" in mock_logger.exception.call_args[0][0]


@pytest.mark.fast
def test_save_logbook_os_error(logbook: lb.Logbook) -> None:
    """Test that save_logbook handles OSError gracefully."""
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
    with patch.object(df, "to_csv", side_effect=OSError("Disk full")), patch("src.logbook.logger") as mock_logger:
        logbook.save_logbook(df)

        # Verify that the exception was logged
        mock_logger.exception.assert_called_once()
        assert "OS error while saving logbook" in mock_logger.exception.call_args[0][0]


@pytest.mark.fast
def test_save_logbook_unexpected_exception(logbook: lb.Logbook) -> None:
    """Test that save_logbook handles unexpected exceptions gracefully."""
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

    # Mock pd.DataFrame.to_csv to raise an unexpected exception
    with patch.object(df, "to_csv", side_effect=Exception("Unexpected error")), patch("src.logbook.logger") as mock_logger:
        logbook.save_logbook(df)

        # Verify that the exception was logged
        mock_logger.exception.assert_called_once()
        assert "Unexpected error saving logbook" in mock_logger.exception.call_args[0][0]


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

import pandas as pd
import pytest

import src.logbook as lb
import src.time_recorder as tr


@pytest.mark.fast
def test_record_into_df_creates_and_appends_row(logbook: lb.Logbook, line: tr.TimeRecorder) -> None:
    """Test that record_into_df creates the file and appends rows correctly as a DataFrame."""
    # Should create file and write header + row
    logbook.record_into_df(line.time_report_line_to_dict())
    assert logbook.get_path().exists()
    df = logbook.load_logbook()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]["date"] == line.date
    assert df.iloc[0]["weekday"] == line.weekday
    # Appending another row should add a new row
    logbook.record_into_df(line.time_report_line_to_dict())
    df2 = logbook.load_logbook()
    assert len(df2) == 2
    assert (df2["date"] == line.date).all()


@pytest.mark.fast
def test_create_df_creates_file_with_correct_columns(logbook: lb.Logbook) -> None:
    """Test that create_df creates a file with the correct columns and no rows."""
    logbook.create_df()
    assert logbook.get_path().exists()
    df = logbook.load_logbook()
    expected_columns = ["weekday", "date", "start_time", "end_time", "lunch_break_duration", "work_time", "case", "overtime"]
    assert list(df.columns) == expected_columns
    assert len(df) == 0

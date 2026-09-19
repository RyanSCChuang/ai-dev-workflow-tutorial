"""Tests for data.py: loading, validating, and summarising the sales data."""
import pandas as pd
import pytest

from data import load_sales

HEADER = "date,order_id,product,category,region,quantity,unit_price,total_amount\n"


def write_csv(tmp_path, body, header=HEADER):
    """Write a small sales CSV into pytest's temporary folder and return its path."""
    path = tmp_path / "sales.csv"
    path.write_text(header + body)
    return path


def test_load_sales_reads_rows_and_parses_dates(tmp_path):
    path = write_csv(tmp_path, "2024-01-03,ORD-1,Phone Case,Accessories,South,3,24.99,74.97\n")
    df = load_sales(path)
    assert len(df) == 1
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df.loc[0, "total_amount"] == pytest.approx(74.97)


def test_load_sales_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_sales(tmp_path / "nope.csv")


def test_load_sales_missing_column_raises_value_error(tmp_path):
    path = write_csv(
        tmp_path,
        "2024-01-03,ORD-1,South,74.97\n",
        header="date,order_id,region,total_amount\n",
    )
    with pytest.raises(ValueError, match="missing columns"):
        load_sales(path)


def test_load_sales_no_rows_raises_value_error(tmp_path):
    path = write_csv(tmp_path, "")
    with pytest.raises(ValueError, match="no rows"):
        load_sales(path)


def test_load_sales_bad_date_raises_value_error(tmp_path):
    path = write_csv(tmp_path, "not-a-date,ORD-1,Phone Case,Accessories,South,3,24.99,74.97\n")
    with pytest.raises(ValueError, match="parse dates"):
        load_sales(path)

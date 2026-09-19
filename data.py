"""Load the sales CSV and compute the numbers and chart series for the dashboard.

Pure pandas: nothing in this file imports Streamlit, so every function can be
tested on its own.
"""
from pathlib import Path

import pandas as pd

# The CSV next to this file, so the app finds it from any working directory.
DEFAULT_PATH = Path(__file__).parent / "data" / "sales-data.csv"

REQUIRED_COLUMNS = [
    "date",
    "order_id",
    "product",
    "category",
    "region",
    "quantity",
    "unit_price",
    "total_amount",
]


def load_sales(path=DEFAULT_PATH):
    """Read the sales CSV into a DataFrame with `date` parsed as a date.

    Raises FileNotFoundError if the file is missing, and ValueError if a
    required column is missing, a date cannot be parsed, or there are no rows.
    """
    path = Path(path)
    # Short "folder/file" label for messages, so no machine-specific path is shown.
    label = f"{path.parent.name}/{path.name}"
    if not path.exists():
        raise FileNotFoundError(f"Sales data file not found: {label}")
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"Sales data file has no rows: {label}") from None
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Sales data file is missing columns: {', '.join(missing)}")
    if df.empty:
        raise ValueError(f"Sales data file has no rows: {label}")
    try:
        df["date"] = pd.to_datetime(df["date"])
    except (ValueError, TypeError) as error:
        raise ValueError(f"Could not parse dates in {label}: {error}") from None
    return df


def total_sales(df):
    """Sum of every order's total_amount."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (each order_id counts once)."""
    return int(df["order_id"].nunique())


def format_currency(value):
    """Whole dollars with thousands separators, e.g. 116500.21 -> $116,500."""
    return f"${value:,.0f}"


def monthly_sales(df):
    """Sales summed per calendar month, oldest first. Columns: month, sales."""
    months = df["date"].dt.to_period("M").dt.to_timestamp()
    result = df.groupby(months)["total_amount"].sum().reset_index()
    result.columns = ["month", "sales"]
    return result


def _sales_by(df, column):
    """Sales summed per value of `column`, highest first. Columns: <column>, sales."""
    result = df.groupby(column)["total_amount"].sum().reset_index()
    result.columns = [column, "sales"]
    return result.sort_values("sales", ascending=False).reset_index(drop=True)


def sales_by_category(df):
    """Sales per product category, highest first."""
    return _sales_by(df, "category")


def sales_by_region(df):
    """Sales per region, highest first."""
    return _sales_by(df, "region")

"""ShopSmart sales dashboard (Streamlit entry point).

Layout only: every number and chart series comes from data.py.
"""
import streamlit as st

from data import DEFAULT_PATH, format_currency, load_sales, total_orders, total_sales

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")


@st.cache_data
def get_sales():
    """Load the sales CSV once and reuse it (keeps page loads fast)."""
    return load_sales(DEFAULT_PATH)


st.title("ShopSmart Sales Dashboard")

# Show one clear message instead of a traceback if the data can't be loaded.
try:
    sales = get_sales()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load the sales data ({DEFAULT_PATH}): {error}")
    st.stop()

st.caption(f"Source: data/sales-data.csv, {len(sales):,} rows")

# KPI row: the two headline numbers.
kpi_sales, kpi_orders = st.columns(2)
kpi_sales.metric("Total Sales", format_currency(total_sales(sales)))
kpi_orders.metric("Total Orders", f"{total_orders(sales):,}")

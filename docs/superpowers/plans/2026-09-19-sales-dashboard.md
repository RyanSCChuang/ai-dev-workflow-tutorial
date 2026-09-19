# ShopSmart Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **For this project the owner has chosen inline execution: no subagents, one milestone at a time, stopping after each milestone for the owner's review.**

**Goal:** Build the PRD's Phase 1 sales dashboard (two KPI cards, a monthly trend line, and sorted category and region bar charts) as a tested Streamlit app, ready for the owner to deploy from `main`.

**Architecture:** `data.py` holds pure pandas functions (load, validate, aggregate, format) with no Streamlit inside, covered by pytest tests written first. `app.py` is layout only: it caches the load, shows a friendly error if the CSV is bad, and draws the KPIs and three Plotly charts from `data.py`'s results.

**Tech Stack:** Python 3.12 or 3.13 in a plain `venv/`, Streamlit, pandas, Plotly Express, pytest.

**Spec:** `docs/superpowers/specs/2026-09-19-sales-dashboard-design.md`
**Milestone board:** `TASKS.md` (TASK-1 to TASK-6). Plan tasks below are numbered **P1 to P11** and each is tagged with its milestone, so the two numbering schemes never mix.

## Global Constraints

- **Repo and branch:** all work is in `/Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial` on branch `feature/sales-dashboard`. No git worktree. The shell resets to a different directory between commands, so **every bash block starts with the `cd` line shown**.
- **Python:** a stable 3.12 or 3.13 only. The machine's default `python3` is 3.15.0rc1, on which `pyarrow` (and therefore Streamlit) does not install.
- **Environment:** plain virtual environment in `venv/` (already covered by `.gitignore`) with one `requirements.txt`. No uv, no conda. Never create `uv.lock`, `Pipfile` or `pyproject.toml` (Streamlit Cloud reads those before `requirements.txt`).
- **Interfaces (exact names):** `data.py` exports `DEFAULT_PATH`, `load_sales`, `total_sales`, `total_orders`, `monthly_sales`, `sales_by_category`, `sales_by_region`, `format_currency`. `data.py` never imports Streamlit.
- **Numbers and labels:** trend chart is monthly (12 points); Total Sales is whole dollars (`$116,500`); Total Orders counts distinct `order_id`; page title is exactly `ShopSmart Sales Dashboard`; bar charts are horizontal, highest bar at the top, tooltips in whole dollars.
- **Errors:** `load_sales` raises `FileNotFoundError` (missing file) or `ValueError` (missing column, unparsable date, no rows). `app.py` catches exactly those two, shows `st.error`, and calls `st.stop()`.
- **Tests:** run with `venv/bin/python -m pytest` from the repo root. Test-first applies only to the `data.py` calculations (tasks flagged **TDD: yes**). Chart and layout code is not unit-tested; it is checked by running the app.
- **Commits:** every commit message starts with its milestone ID (`TASK-N: ...`) and ends with the trailer `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`. Stage files by name.
- **Board bookkeeping is outside this plan.** After each milestone's plan tasks, the executor updates `TASKS.md` (check off criteria, put the last code commit hash on the Commit line, add a Notes line, move to Done) in its own commit `TASK-N: mark done on the board`, and pushes the feature branch.
- **Spec note:** the spec writes the default CSV path as `data/sales-data.csv`. The code resolves it next to `data.py` (`Path(__file__).parent / "data" / "sales-data.csv"`), which is the same file but works from any working directory, including Streamlit Cloud.
- **Deployment is not executed by the agent.** P11 is the owner's.

## File Structure

| File | Responsibility |
|---|---|
| `requirements.txt` (create, P1) | `streamlit`, `pandas`, `plotly`, `pytest` with `>=` pins set to the versions installed and tested |
| `data.py` (create, P2; extend P4, P6, P8) | Load and validate the CSV; every calculation and chart series; currency formatting |
| `tests/test_data.py` (create, P2; extend P4, P6, P8, P10) | pytest tests for `data.py` |
| `app.py` (create, P3; extend P5, P7, P9) | Streamlit page: title, cached load, error handling, KPI row, three charts |

---

### Task P1: Python environment and requirements

**Milestone: TASK-1** | **TDD: no**

**Files:**
- Create: `requirements.txt`
- Create (git-ignored, not committed): `venv/`

**Interfaces:**
- Consumes: nothing.
- Produces: `venv/bin/python`, `venv/bin/pip`, `venv/bin/streamlit`, and `venv/bin/pytest` for every later task; a Streamlit whose `st.plotly_chart` accepts the `width` keyword (P7 and P9 use `width="stretch"`).

- [ ] **Step 1: Find a stable Python and create the venv**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
PY=""
for candidate in \
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 \
  /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 \
  /usr/local/bin/python3.13 \
  /usr/local/bin/python3.12; do
  if [ -x "$candidate" ]; then PY="$candidate"; break; fi
done
if [ -z "$PY" ]; then
  echo "NO STABLE PYTHON FOUND: the owner must install Python 3.12 or 3.13 from python.org. STOP."
  exit 1
fi
"$PY" -m venv venv && venv/bin/python --version
```

Expected: prints `Python 3.13.x` or `Python 3.12.x`. If it prints `NO STABLE PYTHON FOUND`, **stop the whole plan and tell the owner**; do not fall back to 3.15.

- [ ] **Step 2: Install the dependencies**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/pip install streamlit pandas plotly pytest
```

Expected: ends with `Successfully installed ...` and no error.

- [ ] **Step 3: Write `requirements.txt` from the installed versions**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/pip list --format=freeze | grep -i -E '^(streamlit|pandas|plotly|pytest)==' | sed 's/==/>=/' > requirements.txt
cat requirements.txt
```

Expected: exactly four lines, one each for `pandas`, `plotly`, `pytest`, `streamlit`, in the form `name>=X.Y.Z`.

- [ ] **Step 4: Check that this Streamlit accepts `width` on `st.plotly_chart`**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -c "import inspect, streamlit as st; assert 'width' in inspect.signature(st.plotly_chart).parameters; print('OK: plotly_chart accepts width; streamlit', st.__version__)"
```

Expected: `OK: plotly_chart accepts width; streamlit <version>`. If the assertion fails, **stop and report** (P7 and P9 depend on it).

- [ ] **Step 5: Confirm `venv/` is git-ignored**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git check-ignore -v venv/ && git status --short
```

Expected: a line naming the `.gitignore` rule for `venv/`, then a status showing only `?? requirements.txt`.

- [ ] **Step 6: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add requirements.txt
git commit -m "$(cat <<'EOF'
TASK-1: add requirements.txt for Streamlit, pandas, plotly, pytest

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task P2: Load and validate the sales CSV

**Milestone: TASK-1** | **TDD: yes**

**Files:**
- Create: `data.py`
- Create: `tests/test_data.py`

**Interfaces:**
- Consumes: `data/sales-data.csv`; the venv from P1.
- Produces: `DEFAULT_PATH` (a `pathlib.Path` to the CSV next to `data.py`); `load_sales(path=DEFAULT_PATH) -> pandas.DataFrame` with all 8 columns and `date` parsed as datetime; raises `FileNotFoundError` for a missing file and `ValueError` for a missing column, unparsable date, or no rows.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_data.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest tests/test_data.py -v
```

Expected: collection ERROR `ModuleNotFoundError: No module named 'data'` (no `data.py` yet).

- [ ] **Step 3: Write the minimal implementation**

Create `data.py`:

```python
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
    if not path.exists():
        raise FileNotFoundError(f"Sales data file not found: {path}")
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"Sales data file has no rows: {path}") from None
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Sales data file is missing columns: {', '.join(missing)}")
    if df.empty:
        raise ValueError(f"Sales data file has no rows: {path}")
    try:
        df["date"] = pd.to_datetime(df["date"])
    except (ValueError, TypeError) as error:
        raise ValueError(f"Could not parse dates in {path}: {error}") from None
    return df
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest tests/test_data.py -v
```

Expected: `5 passed`.

- [ ] **Step 5: Confirm the real CSV loads**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -c "from data import load_sales; df = load_sales(); print(len(df), df['date'].min().date(), df['date'].max().date())"
```

Expected: `482 2024-01-03 2024-12-31`.

- [ ] **Step 6: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add data.py tests/test_data.py
git commit -m "$(cat <<'EOF'
TASK-1: load and validate the sales CSV

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task P3: App skeleton with title, cached load, and friendly error

**Milestone: TASK-1** | **TDD: no** (page layout is checked by running the app)

**Files:**
- Create: `app.py`

**Interfaces:**
- Consumes: `DEFAULT_PATH`, `load_sales` from `data.py` (P2).
- Produces: a runnable `app.py` that defines `get_sales()` (cached load) and the variable `sales` (the loaded DataFrame) at module level; later tasks append to the end of this file and use `sales`.

- [ ] **Step 1: Create `app.py`**

```python
"""ShopSmart sales dashboard (Streamlit entry point).

Layout only: every number and chart series comes from data.py.
"""
import streamlit as st

from data import DEFAULT_PATH, load_sales

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
```

- [ ] **Step 2: Smoke-check the happy path**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python - <<'EOF'
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py").run(timeout=30)
assert not at.exception, at.exception
assert at.title[0].value == "ShopSmart Sales Dashboard"
assert at.caption[0].value == "Source: data/sales-data.csv, 482 rows"
print("happy path OK")
EOF
```

Expected: `happy path OK`.

- [ ] **Step 3: Smoke-check the missing-file path (restores the file in `finally`)**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python - <<'EOF'
from pathlib import Path
from streamlit.testing.v1 import AppTest

data = Path("data/sales-data.csv")
backup = Path("data/sales-data.csv.bak")
data.rename(backup)
try:
    at = AppTest.from_file("app.py").run(timeout=30)
    assert not at.exception, at.exception
    assert len(at.error) == 1, "expected exactly one friendly error message"
    assert "Could not load the sales data" in at.error[0].value
    print("missing-file path OK:", at.error[0].value)
finally:
    backup.rename(data)
EOF
git status --short
```

Expected: `missing-file path OK: Could not load the sales data (...sales-data.csv): Sales data file not found: ...`, then `git status --short` prints only `?? app.py` (the CSV is back and unchanged).

- [ ] **Step 4: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add app.py
git commit -m "$(cat <<'EOF'
TASK-1: add Streamlit app with title, cached data load, and friendly error

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 5: Run the app for the owner (stop any running server first)**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
pkill -f "streamlit run" || true
venv/bin/streamlit run app.py --server.headless true --server.port 8501
```

Run this in the background. Then `curl -s http://localhost:8501/_stcore/health` should print `ok`. Tell the owner to open `http://localhost:8501` and confirm they see the title "ShopSmart Sales Dashboard" and the caption "Source: data/sales-data.csv, 482 rows".

**STOP after this task and ask the owner to review the TASK-1 diff** (`git diff main...HEAD -- app.py data.py`) before the board update and TASK-2. Then do the TASK-1 board update and push (see Global Constraints).

---

### Task P4: KPI calculations

**Milestone: TASK-2** | **TDD: yes**

**Files:**
- Modify: `data.py` (append functions)
- Modify: `tests/test_data.py` (edit the import line; append tests)

**Interfaces:**
- Consumes: `data.py` module from P2; DataFrames with columns `order_id` and `total_amount`.
- Produces: `total_sales(df) -> float`, `total_orders(df) -> int`, `format_currency(value) -> str`; and, in the test file, the helper `make_sales(rows)` used by later tests.

- [ ] **Step 1: Write the failing tests**

In `tests/test_data.py`, replace the line `from data import load_sales` with:

```python
from data import format_currency, load_sales, total_orders, total_sales
```

Then append to the end of the file:

```python
def make_sales(rows):
    """Build a small sales DataFrame from (date, order_id, category, region, total_amount) rows."""
    df = pd.DataFrame(rows, columns=["date", "order_id", "category", "region", "total_amount"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_total_sales_adds_every_order():
    df = make_sales([
        ("2024-01-05", "A", "Audio", "North", 100.50),
        ("2024-01-20", "B", "Wearables", "South", 25.25),
    ])
    assert total_sales(df) == pytest.approx(125.75)


def test_total_orders_counts_each_order_once():
    df = make_sales([
        ("2024-01-05", "A", "Audio", "North", 10.0),
        ("2024-01-05", "A", "Audio", "North", 10.0),
        ("2024-01-06", "B", "Audio", "North", 10.0),
    ])
    assert total_orders(df) == 2


def test_format_currency_adds_symbol_and_separators():
    assert format_currency(1234567) == "$1,234,567"


def test_format_currency_rounds_to_whole_dollars():
    assert format_currency(116500.21) == "$116,500"
    assert format_currency(999.6) == "$1,000"


def test_format_currency_handles_small_and_zero_values():
    assert format_currency(42) == "$42"
    assert format_currency(0) == "$0"
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest tests/test_data.py -v
```

Expected: collection ERROR `ImportError: cannot import name 'format_currency' from 'data'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `data.py`:

```python


def total_sales(df):
    """Sum of every order's total_amount."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (each order_id counts once)."""
    return int(df["order_id"].nunique())


def format_currency(value):
    """Whole dollars with thousands separators, e.g. 116500.21 -> $116,500."""
    return f"${value:,.0f}"
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest tests/test_data.py -v
```

Expected: `10 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add data.py tests/test_data.py
git commit -m "$(cat <<'EOF'
TASK-2: add total_sales, total_orders, and format_currency with tests

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task P5: KPI scorecards on the page

**Milestone: TASK-2** | **TDD: no**

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `format_currency`, `total_orders`, `total_sales` (P4); the module-level `sales` DataFrame (P3).
- Produces: two `st.metric` cards labelled `Total Sales` and `Total Orders`.

- [ ] **Step 1: Update the import in `app.py`**

Replace the line `from data import DEFAULT_PATH, load_sales` with:

```python
from data import DEFAULT_PATH, format_currency, load_sales, total_orders, total_sales
```

- [ ] **Step 2: Append the KPI row to the end of `app.py`**

```python

# KPI row: the two headline numbers.
kpi_sales, kpi_orders = st.columns(2)
kpi_sales.metric("Total Sales", format_currency(total_sales(sales)))
kpi_orders.metric("Total Orders", f"{total_orders(sales):,}")
```

- [ ] **Step 3: Smoke-check the page**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python - <<'EOF'
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py").run(timeout=30)
assert not at.exception, at.exception
values = {m.label: m.value for m in at.metric}
assert values == {"Total Sales": "$116,500", "Total Orders": "482"}, values
print("KPIs OK:", values)
EOF
```

Expected: `KPIs OK: {'Total Sales': '$116,500', 'Total Orders': '482'}`.

- [ ] **Step 4: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add app.py
git commit -m "$(cat <<'EOF'
TASK-2: show Total Sales and Total Orders KPI cards

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 5: Run the app for the owner (stop any running server first)**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
pkill -f "streamlit run" || true
venv/bin/streamlit run app.py --server.headless true --server.port 8501
```

Run in the background, confirm `curl -s http://localhost:8501/_stcore/health` prints `ok`, and tell the owner to open `http://localhost:8501` and confirm two cards: Total Sales `$116,500` and Total Orders `482`. Then do the TASK-2 board update and push.

---

### Task P6: Monthly sales series

**Milestone: TASK-3** | **TDD: yes**

**Files:**
- Modify: `data.py` (append)
- Modify: `tests/test_data.py` (edit import line; append test)

**Interfaces:**
- Consumes: DataFrames with columns `date` (datetime) and `total_amount`; `make_sales` helper (P4).
- Produces: `monthly_sales(df) -> DataFrame` with columns `month` (Timestamp, first day of the month) and `sales`, one row per calendar month present in the data, oldest first.

- [ ] **Step 1: Write the failing test**

In `tests/test_data.py`, replace the import line `from data import format_currency, load_sales, total_orders, total_sales` with:

```python
from data import format_currency, load_sales, monthly_sales, total_orders, total_sales
```

Append to the end of the file:

```python
def test_monthly_sales_sums_each_month_oldest_first():
    df = make_sales([
        ("2024-02-10", "A", "Audio", "North", 50.0),
        ("2024-01-05", "B", "Audio", "North", 100.0),
        ("2024-01-20", "C", "Wearables", "South", 25.0),
    ])
    result = monthly_sales(df)
    assert list(result.columns) == ["month", "sales"]
    assert list(result["month"]) == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-02-01")]
    assert list(result["sales"]) == [125.0, 50.0]
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest tests/test_data.py -v
```

Expected: collection ERROR `ImportError: cannot import name 'monthly_sales' from 'data'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `data.py`:

```python


def monthly_sales(df):
    """Sales summed per calendar month, oldest first. Columns: month, sales."""
    months = df["date"].dt.to_period("M").dt.to_timestamp()
    result = df.groupby(months)["total_amount"].sum().reset_index()
    result.columns = ["month", "sales"]
    return result
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest tests/test_data.py -v
```

Expected: `11 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add data.py tests/test_data.py
git commit -m "$(cat <<'EOF'
TASK-3: add monthly_sales with test

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task P7: Sales trend chart

**Milestone: TASK-3** | **TDD: no**

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `monthly_sales` (P6); the `sales` DataFrame (P3); Streamlit with `width` support on `st.plotly_chart` (verified in P1).
- Produces: one full-width Plotly line chart titled `Sales Trend by Month`.

- [ ] **Step 1: Update the imports in `app.py`**

Replace the line `import streamlit as st` with:

```python
import plotly.express as px
import streamlit as st
```

Replace the line `from data import DEFAULT_PATH, format_currency, load_sales, total_orders, total_sales` with:

```python
from data import (
    DEFAULT_PATH,
    format_currency,
    load_sales,
    monthly_sales,
    total_orders,
    total_sales,
)
```

- [ ] **Step 2: Append the trend chart to the end of `app.py`**

```python

# Sales trend: one point per month, tooltip shows the month and exact dollars.
trend = monthly_sales(sales)
trend_fig = px.line(
    trend,
    x="month",
    y="sales",
    markers=True,
    title="Sales Trend by Month",
    labels={"month": "Month", "sales": "Sales ($)"},
)
trend_fig.update_xaxes(tickformat="%b %Y", dtick="M1")
trend_fig.update_yaxes(tickprefix="$", tickformat=",")
trend_fig.update_traces(hovertemplate="%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>")
st.plotly_chart(trend_fig, width="stretch")
```

- [ ] **Step 3: Smoke-check the page**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python - <<'EOF'
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py").run(timeout=30)
assert not at.exception, at.exception
assert len(at.get("plotly_chart")) == 1, "expected one chart"
assert len(at.metric) == 2, "KPI cards must still be present"
print("trend chart OK")
EOF
```

Expected: `trend chart OK`.

- [ ] **Step 4: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add app.py
git commit -m "$(cat <<'EOF'
TASK-3: add monthly sales trend line chart

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 5: Run the app for the owner (stop any running server first)**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
pkill -f "streamlit run" || true
venv/bin/streamlit run app.py --server.headless true --server.port 8501
```

Run in the background, confirm `curl -s http://localhost:8501/_stcore/health` prints `ok`, and tell the owner to open `http://localhost:8501` and confirm a 12-point line (Jan 2024 to Dec 2024) whose tooltip shows a month and a dollar amount. Then do the TASK-3 board update and push.

---

### Task P8: Category and region series

**Milestone: TASK-4** | **TDD: yes**

**Files:**
- Modify: `data.py` (append)
- Modify: `tests/test_data.py` (edit import line; append tests)

**Interfaces:**
- Consumes: DataFrames with columns `category`, `region`, `total_amount`; `make_sales` (P4).
- Produces: `sales_by_category(df)` and `sales_by_region(df)`, each a DataFrame with columns (`category` or `region`) and `sales`, one row per group present, sorted highest sales first.

- [ ] **Step 1: Write the failing tests**

In `tests/test_data.py`, replace the import line `from data import format_currency, load_sales, monthly_sales, total_orders, total_sales` with:

```python
from data import (
    format_currency,
    load_sales,
    monthly_sales,
    sales_by_category,
    sales_by_region,
    total_orders,
    total_sales,
)
```

Append to the end of the file:

```python
def test_sales_by_category_sums_and_sorts_highest_first():
    df = make_sales([
        ("2024-01-05", "A", "Accessories", "North", 10.0),
        ("2024-01-06", "B", "Electronics", "North", 300.0),
        ("2024-01-07", "C", "Audio", "South", 50.0),
        ("2024-01-08", "D", "Audio", "South", 70.0),
    ])
    result = sales_by_category(df)
    assert list(result.columns) == ["category", "sales"]
    assert list(result["category"]) == ["Electronics", "Audio", "Accessories"]
    assert list(result["sales"]) == [300.0, 120.0, 10.0]


def test_sales_by_region_sums_and_sorts_highest_first():
    df = make_sales([
        ("2024-01-05", "A", "Audio", "West", 40.0),
        ("2024-01-06", "B", "Audio", "North", 90.0),
        ("2024-01-07", "C", "Audio", "West", 30.0),
        ("2024-01-08", "D", "Audio", "South", 5.0),
    ])
    result = sales_by_region(df)
    assert list(result.columns) == ["region", "sales"]
    assert list(result["region"]) == ["North", "West", "South"]
    assert list(result["sales"]) == [90.0, 70.0, 5.0]
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest tests/test_data.py -v
```

Expected: collection ERROR `ImportError: cannot import name 'sales_by_category' from 'data'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `data.py`:

```python


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
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest tests/test_data.py -v
```

Expected: `13 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add data.py tests/test_data.py
git commit -m "$(cat <<'EOF'
TASK-4: add sales_by_category and sales_by_region with tests

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task P9: Category and region bar charts

**Milestone: TASK-4** | **TDD: no**

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_by_category`, `sales_by_region` (P8); `px` and `sales` (P3, P7).
- Produces: `sales_bar_chart(data, column, title)` helper and two side-by-side horizontal bar charts, highest bar at the top.

- [ ] **Step 1: Update the data import in `app.py`**

Replace the multi-line block starting `from data import (` and ending `)` with:

```python
from data import (
    DEFAULT_PATH,
    format_currency,
    load_sales,
    monthly_sales,
    sales_by_category,
    sales_by_region,
    total_orders,
    total_sales,
)
```

- [ ] **Step 2: Add the bar-chart helper**

Insert directly after the `get_sales` function (and before the line `st.title("ShopSmart Sales Dashboard")`):

```python
def sales_bar_chart(data, column, title):
    """Horizontal bars of sales, highest bar at the top, tooltips in whole dollars."""
    fig = px.bar(
        data,
        x="sales",
        y=column,
        orientation="h",
        title=title,
        labels={"sales": "Sales ($)", column: column.title()},
    )
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_xaxes(tickprefix="$", tickformat=",")
    fig.update_traces(hovertemplate="%{y}<br>$%{x:,.0f}<extra></extra>")
    return fig


```

- [ ] **Step 3: Append the two charts to the end of `app.py`**

```python

# Breakdowns: sales by category and by region, side by side.
category_col, region_col = st.columns(2)
category_col.plotly_chart(
    sales_bar_chart(sales_by_category(sales), "category", "Sales by Category"),
    width="stretch",
)
region_col.plotly_chart(
    sales_bar_chart(sales_by_region(sales), "region", "Sales by Region"),
    width="stretch",
)
```

- [ ] **Step 4: Smoke-check the page**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python - <<'EOF'
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py").run(timeout=30)
assert not at.exception, at.exception
assert len(at.get("plotly_chart")) == 3, "expected trend + category + region charts"
assert len(at.metric) == 2, "KPI cards must still be present"
print("all three charts OK")
EOF
```

Expected: `all three charts OK`.

- [ ] **Step 5: Commit**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add app.py
git commit -m "$(cat <<'EOF'
TASK-4: add sorted category and region bar charts

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 6: Run the app for the owner (stop any running server first)**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
pkill -f "streamlit run" || true
venv/bin/streamlit run app.py --server.headless true --server.port 8501
```

Run in the background, confirm `curl -s http://localhost:8501/_stcore/health` prints `ok`, and tell the owner to open `http://localhost:8501` and confirm two horizontal bar charts: 5 categories with Electronics on top, and 4 regions with North on top, each tooltip showing a whole-dollar amount. Then do the TASK-4 board update and push.

---

### Task P10: Verify against the PRD and polish

**Milestone: TASK-5** | **TDD: no** (this task adds a verification test of already-built behaviour, so it should pass on its first run)

**Files:**
- Modify: `tests/test_data.py` (append one test)
- Modify (only if a check below fails): `data.py`, `app.py`

**Interfaces:**
- Consumes: every function in `data.py` (P2, P4, P6, P8); the full `app.py` (P3, P5, P7, P9).
- Produces: a real-data regression test; evidence that every PRD Acceptance Criterion, NFR-1 (load speed), and NFR-3 (documentation) hold.

- [ ] **Step 1: Add the real-data test**

In `tests/test_data.py`, append to the end of the file:

```python
def test_real_data_matches_the_prd_expected_output():
    df = load_sales()
    assert total_orders(df) == 482
    assert total_sales(df) == pytest.approx(116500.21, abs=0.01)
    assert format_currency(total_sales(df)) == "$116,500"
    categories = sales_by_category(df)
    assert len(categories) == 5
    assert categories["category"].iloc[0] == "Electronics"
    regions = sales_by_region(df)
    assert len(regions) == 4
    assert regions["region"].iloc[0] == "North"
    assert len(monthly_sales(df)) == 12
```

- [ ] **Step 2: Run the full test suite**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python -m pytest -v
```

Expected: `14 passed`.

- [ ] **Step 3: Check the whole page for errors, values, and load time (NFR-1)**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python - <<'EOF'
import time
from streamlit.testing.v1 import AppTest

start = time.time()
at = AppTest.from_file("app.py").run(timeout=30)
elapsed = time.time() - start
assert not at.exception, at.exception
assert not at.error, [e.value for e in at.error]
assert not at.warning, [w.value for w in at.warning]
assert at.title[0].value == "ShopSmart Sales Dashboard"
assert {m.label: m.value for m in at.metric} == {"Total Sales": "$116,500", "Total Orders": "482"}
assert len(at.get("plotly_chart")) == 3
assert elapsed < 5, f"page took {elapsed:.1f}s (PRD target: under 5s)"
print(f"page OK in {elapsed:.1f}s")
EOF
```

Expected: `page OK in <n>s` with n under 5.

- [ ] **Step 4: Check every function is documented (NFR-3)**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
venv/bin/python - <<'EOF'
import ast

for name in ("data.py", "app.py"):
    tree = ast.parse(open(name).read())
    missing = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node)
    ]
    print(name, "functions without a docstring:", missing)
    assert not missing
EOF
```

Expected: both lines end with `[]`. If any function is listed, add a one-line docstring to it and re-run.

- [ ] **Step 5: Check the server log for warnings (PRD "no errors or warnings")**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
pkill -f "streamlit run" || true
venv/bin/streamlit run app.py --server.headless true --server.port 8501
```

Run in the background. Load the page once with `curl -s http://localhost:8501/ > /dev/null`, then read the server's output. Expected: no lines containing `Warning`, `Deprecat`, or `Traceback`. If any appear, fix the cause in `app.py` and re-run Steps 3 and 5.

- [ ] **Step 6: Commit the real-data test (plus any fixes from Steps 3 to 5, in their own commits)**

```bash
cd /Users/ryan.alois.sky/GitHub/ai-dev-workflow-tutorial
git add tests/test_data.py
git commit -m "$(cat <<'EOF'
TASK-5: add real-data test against the PRD's expected output

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

Any fix made in Steps 3 to 5 gets its own commit with a message like `TASK-5: fix <what was wrong>`.

- [ ] **Step 7: Owner acceptance walk-through (the owner does this by eye, without asking the agent)**

With the app still running at `http://localhost:8501`, the owner checks each PRD Acceptance Criterion against what is on screen:

| # | PRD Acceptance Criterion | What to look for |
|---|---|---|
| 1 | KPIs visible | Total Sales `$116,500` and Total Orders `482`, prominently at the top |
| 2 | Trend chart works | 12-point monthly line, Jan to Dec 2024, tooltip shows month and dollars |
| 3 | Category chart works | 5 bars, Electronics highest at the top, sorted high to low |
| 4 | Region chart works | 4 bars, North highest at the top, sorted high to low |
| 5 | Data loads correctly | Numbers match the PRD's expected output (about $116,500, 482 orders) |
| 6 | No errors | No red error box; the browser shows no warnings |
| 7 | Professional appearance | Clear titles and axis labels; suitable for an executive meeting |

Also (NFR-4): the owner opens the same URL in a second browser (for example Safari and Chrome) and confirms it renders. Anything that fails goes back to the agent as a plain request, fixed under a `TASK-5:` commit, then re-checked. Then do the TASK-5 board update and push.

---

### Task P11: Deploy to Streamlit Community Cloud

**Milestone: TASK-6** | **TDD: no** | **OWNER'S TASK: the agent does NOT execute this.**

> **HANDOFF. The plan stops here.** Publishing needs the owner's GitHub and Streamlit accounts and a go/no-go decision. The agent's job ends at handing these steps over, and resumes only when the owner returns with the live URL (Step 8). TASK-6 stays in **To Do** on `TASKS.md` until then.

**Prerequisite:** the feature branch has been reviewed (`/code-review`), the fixes committed, `CLAUDE.md` added, and `feature/sales-dashboard` merged into `main` with a merge commit and pushed. Streamlit Cloud deploys from `main`.

**Files:** none (the owner works in a browser).

- [ ] **Step 1 (owner):** Open https://share.streamlit.io and click **Continue to sign-in**, then **Continue with GitHub**, and authorize Streamlit.
- [ ] **Step 2 (owner, first time only):** Verify your email with the 6-digit code, authorize Streamlit's broader GitHub permissions, and complete the short account form (choose **Student** as functional area).
- [ ] **Step 3 (owner):** Click **Create app**, then **Deploy a public app from GitHub**.
- [ ] **Step 4 (owner):** Fill in the form:

| Field | Value |
|---|---|
| Repository | `RyanSCChuang/ai-dev-workflow-tutorial` |
| Branch | `main` |
| Main file path | `app.py` |
| App URL (optional) | a slug such as `sales-dashboard-ryanchuang` |

- [ ] **Step 5 (owner):** Under **Advanced settings**, choose Python 3.12 or 3.13 (the same family the app was built on locally).
- [ ] **Step 6 (owner):** Click **Deploy** and wait 1 to 2 minutes while Streamlit Cloud installs `requirements.txt` and starts the app.
- [ ] **Step 7 (owner):** Open the resulting URL (for example `https://sales-dashboard-ryanchuang.streamlit.app`) and confirm it looks and behaves like the local version: same KPIs, three charts, no error box.
- [ ] **Step 8 (owner, then agent):** Give the agent the live URL. The agent then records it next to TASK-6 in `TASKS.md`, checks off its criteria, moves it to Done, adds the same URL near the top of `README.md`, commits both files, and pushes `main`.

If deployment fails, the usual cause is `requirements.txt` missing or wrong on `main`, or a stray `uv.lock`, `Pipfile`, or `pyproject.toml` in the repo. Report the exact error to the agent, which fixes it on a branch or on `main` as you direct, then redeploy.

---

## Self-Review Notes

- **Spec coverage:** FR-5 → P2, P3 (TASK-1). FR-1 → P4, P5 (TASK-2). FR-2 → P6, P7 (TASK-3). FR-3 and FR-4 → P8, P9 (TASK-4). NFR-1 → cached load in P3, timed in P10. NFR-2 → titles, axis labels and tooltips in P7 and P9, owner check in P10. NFR-3 → docstrings and comments throughout, checked in P10 Step 4. NFR-4 → P10 Step 7. NFR-5 → P11. PRD Acceptance Criteria and Expected Output → P10. Environment and Python constraint → P1. Deployment boundary → P11.
- **Interface consistency:** function names and signatures match across tasks: `load_sales(path=DEFAULT_PATH)`, `total_sales`, `total_orders`, `format_currency`, `monthly_sales` (columns `month`, `sales`), `sales_by_category` (columns `category`, `sales`), `sales_by_region` (columns `region`, `sales`), `sales_bar_chart(data, column, title)`, `make_sales` test helper.
- **Test counts:** P2 = 5, P4 = 10, P6 = 11, P8 = 13, P10 = 14.

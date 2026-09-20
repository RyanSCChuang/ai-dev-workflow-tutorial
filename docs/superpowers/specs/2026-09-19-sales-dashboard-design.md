# Design: ShopSmart Sales Dashboard

**Date:** 2026-09-19
**Status:** Approved and implemented on `feature/sales-dashboard`. Where the built code differs from the text below, see "Post-build amendments" at the end.
**Source requirements:** `prd/ecommerce-analytics.md` (Phase 1 only)
**Milestone board:** `TASKS.md` (TASK-1 to TASK-6)

## Purpose

Build the Phase 1 sales dashboard described in the PRD: a Streamlit app that
loads `data/sales-data.csv` and shows two KPI scorecards (Total Sales, Total
Orders), a monthly sales trend line, and sorted bar charts of sales by
category and by region. Deploy it to Streamlit Community Cloud so a public URL
exists for stakeholder review.

The app is deliberately small. The point of the project is the workflow
(PRD, board, design, plan, tested build, review, merge, deploy), so the code
stays simple and readable.

## Scope

**In scope (PRD Phase 1):** FR-1 to FR-5 and NFR-1 to NFR-5.

**Out of scope (PRD Phase 2):** authentication, database integration, export,
alerts, filtering and date-range selection, drill-down, mobile-responsive
design. No feature beyond the PRD is added.

## Data (verified against the CSV)

- `data/sales-data.csv`: 482 rows, 482 distinct `order_id`s, no empty cells.
- Columns: `date`, `order_id`, `product`, `category`, `region`, `quantity`,
  `unit_price`, `total_amount`.
- Dates run 2024-01-03 to 2024-12-31, about 40 orders per month.
- `quantity x unit_price` equals `total_amount` on every row.
- Sum of `total_amount` is 116,500.21, matching the PRD's expected ~$116,500.
- 5 categories (Electronics, Wearables, Audio, Smart Home, Accessories) and
  4 regions (North, West, East, South).

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Trend chart granularity | Monthly (12 points) | About 1.3 orders a day would make a daily line jagged; monthly shows the trend the CEO story needs |
| Missing or unreadable CSV | Friendly red error naming the path, then stop | Meets "handles a missing file cleanly" with the least code; an upload box is a PRD Phase 2 feature |
| File layout | `app.py` + `data.py` + tests | Small enough to read in one sitting; calculations testable without Streamlit |
| Total Sales display | Whole dollars, `$116,500` | PRD format is `$X,XXX,XXX`; cents add noise on a scorecard |
| Charting | Streamlit + Plotly Express | The PRD's stack; built-in tooltips; exact control of sort order and `$` hover text |
| Total Orders definition | Count of distinct `order_id` | The correct meaning of "orders"; equals the row count (482) in this file |
| Title | "ShopSmart Sales Dashboard" | The PRD summary names the company ShopSmart; its layout sketch says "SHOPMART", which is treated as a typo |

## Architecture

```
data/sales-data.csv
        |
        v
data.py: load_sales()  -->  DataFrame  -->  total_sales, total_orders,
                                            monthly_sales, sales_by_category,
                                            sales_by_region, format_currency
        |
        v
app.py: cached load, error handling, KPI row, three Plotly charts
        |
        v
Streamlit renders the page in the browser
```

### Files

| File | Responsibility | Depends on |
|---|---|---|
| `data.py` | Load and validate the CSV; compute every number and chart series. Pure pandas, no Streamlit imports. | pandas |
| `app.py` | Page layout, caching, error display, Plotly figures. No calculations of its own. | streamlit, plotly, `data.py` |
| `tests/test_data.py` | pytest tests for everything in `data.py`. | pytest, `data.py` |
| `requirements.txt` | Runtime and test dependencies (`streamlit`, `pandas`, `plotly`, `pytest`) with minimum-version pins set to the versions installed and tested. Streamlit Cloud reads this at deploy. | none |

No `uv.lock`, `Pipfile` or `pyproject.toml` is created, because Streamlit Cloud
reads those before `requirements.txt`. The virtual environment lives in
`venv/`, which `.gitignore` already covers.

### `data.py` interface

| Function | Returns | Behaviour |
|---|---|---|
| `load_sales(path="data/sales-data.csv")` | DataFrame | Reads the CSV, parses `date` as a date. Raises `FileNotFoundError` if the file is missing; raises `ValueError` if a required column is missing, a date cannot be parsed, or there are no rows. |
| `total_sales(df)` | float | Sum of `total_amount`. |
| `total_orders(df)` | int | Number of distinct `order_id` values. |
| `monthly_sales(df)` | DataFrame (`month`, `sales`) | Sales summed per calendar month, sorted oldest to newest. |
| `sales_by_category(df)` | DataFrame (`category`, `sales`) | Sales summed per category, sorted highest to lowest, every category present. |
| `sales_by_region(df)` | DataFrame (`region`, `sales`) | Sales summed per region, sorted highest to lowest, every region present. |
| `format_currency(value)` | str | Whole dollars with thousands separators, e.g. `116500.21` becomes `$116,500`. |

### `app.py` behaviour

1. Set the page title and a wide layout; show "ShopSmart Sales Dashboard".
2. Load the data through a `st.cache_data` wrapper around `load_sales`
   (helps the 5-second load target, NFR-1). The wrapper lives in `app.py` so
   `data.py` stays free of Streamlit.
3. If loading raises `FileNotFoundError` or `ValueError`, show `st.error` with
   the expected path and the problem, then `st.stop()`.
4. KPI row: two `st.metric` cards, Total Sales (`format_currency`) and Total
   Orders (thousands separator).
5. Trend chart: full-width Plotly line with markers, month labels like
   "Jan 2024", tooltip showing the month and exact sales.
6. Two side-by-side horizontal bar charts, sales by category and by region,
   highest bar at the top, tooltips showing exact dollars, axis titles set.

## Error handling

Only failures that can actually happen are handled: a missing or unreadable
CSV, missing columns, unparsable dates, an empty file. Each becomes one clear
message in the app, not a traceback. Nothing else is defended against; the
shipped data is clean and validated above.

## Testing

Test-first (TDD) applies to the calculations in `data.py`, the pieces short
enough to specify completely. Tests use tiny hand-built DataFrames so each
expected value can be checked by eye:

- `total_sales` and `total_orders` (including that duplicate `order_id`s count
  once).
- `monthly_sales` (one row per month, chronological, correct sums).
- `sales_by_category` and `sales_by_region` (correct sums, descending order,
  no group dropped).
- `format_currency` (rounding, separators, values under 1,000).
- `load_sales` (parses dates; raises `FileNotFoundError` for a missing file and
  `ValueError` for a missing column or empty file).

One test runs against the real CSV: 482 orders, sales rounding to $116,500,
5 categories, 4 regions, 12 months, Electronics the top category, North the
top region.

Chart drawing and page layout are not unit-tested; Streamlit components do not
test meaningfully. They are verified by running the app and checking each PRD
Acceptance Criterion by eye. Tests run with `python -m pytest` from the repo
root.

## Environment and deployment boundary

- Plain virtual environment in `venv/` with `requirements.txt`. No uv or conda.
- Requires a stable Python 3.12 or 3.13. The machine's Python 3.15.0rc1 is a
  release candidate on which `pyarrow`, and therefore Streamlit, does not
  install. A stable interpreter must be available before TASK-1's environment
  setup.
- Work happens on branch `feature/sales-dashboard`; no git worktree.
- **Deployment is the final plan step and belongs to the project owner.** It is
  run by hand on Streamlit Community Cloud from the `main` branch after the
  feature branch is reviewed and merged. The plan stops there and hands off;
  it does not deploy. TASK-6 stays in To Do until then.

## Requirements traceability

| Requirement | Delivered by |
|---|---|
| FR-5 Data source (CSV, date/numeric/categorical) | TASK-1: `load_sales`, friendly error |
| FR-1 KPI display, currency formatting | TASK-2: `total_sales`, `total_orders`, `format_currency` |
| FR-2 Sales trend line with tooltips | TASK-3: `monthly_sales`, Plotly line |
| FR-3 Category breakdown, sorted, tooltips | TASK-4: `sales_by_category` |
| FR-4 Regional breakdown, sorted, tooltips | TASK-4: `sales_by_region` |
| NFR-1 Performance (5 s load) | Cached load; timed in TASK-5 |
| NFR-2 Usability, clear labels, professional look | Titles, axis labels, tooltips; reviewed in TASK-5 |
| NFR-3 Maintainability | Two modules, comments, tests |
| NFR-4 Browser compatibility | Manual smoke check in TASK-5 |
| NFR-5 Deployment to Streamlit Community Cloud | TASK-6, run by the owner |
| PRD Acceptance Criteria (7 items) | TASK-5: checked against the running app |
| PRD Expected Output (~$116,500, 482 orders) | Real-data test and TASK-5 check |

## Non-goals

- Anything in PRD Phase 2 (see Scope).
- Date-range filtering, a file-upload fallback, or extra charts.
- Automated tests of Streamlit rendering.

## Post-build amendments (2026-09-20)

The text above is the design as approved. These points record where the built code deliberately differs from it, so the spec and the code agree.

- **Error message shows a short label, not the expected path.** The Decisions table and the `app.py` behaviour list say the friendly error names the expected path. As built, `load_sales` messages use a short `folder/file` label (`data/sales-data.csv`) and `app.py` prints the message once, so no machine-specific path appears on a public deployment. Decided in TASK-5 (commit `2483d48`), test-first.
- **Default CSV path resolves next to `data.py`.** The interface table shows `load_sales(path="data/sales-data.csv")`. As built, `DEFAULT_PATH = Path(__file__).parent / "data" / "sales-data.csv"`: the same file, but found from any working directory, including Streamlit Cloud.
- **Python version.** The Environment section requires a stable 3.12 or 3.13. The tutorial guide requires 3.11 or higher, so 3.11 to 3.13 is acceptable. The build used a checksum-verified standalone Python 3.12.14, because the machine's default 3.15.0rc1 cannot install Streamlit (no `pyarrow` build).

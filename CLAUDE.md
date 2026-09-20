# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A ShopSmart e-commerce sales dashboard (Streamlit + Plotly + pandas) built from `prd/ecommerce-analytics.md`, Phase 1 only. The repo is also a course tutorial: `README.md`, `pre-work-setup.md`, `workshop-build-deploy.md`, `codex-companion.md`, `capstone-tools.md` and `prd/` are upstream course material, so don't edit them. The design lives in `docs/superpowers/specs/`, the implementation plan in `docs/superpowers/plans/`.

## Commands

Everything runs from the repo root (`data.py` is imported as a top-level module, so tests and the app break from other directories).

```bash
# one-time setup: build venv/ from a STABLE Python (see Environment), then install
~/.local/python-3.12-standalone/python/bin/python3.12 -m venv venv
venv/bin/pip install -r requirements.txt

# run the dashboard (default http://localhost:8501)
venv/bin/streamlit run app.py --server.headless true --server.port 8501

# tests
venv/bin/python -m pytest
venv/bin/python -m pytest tests/test_data.py::test_total_orders_counts_each_order_once -v   # one test
```

No linter or formatter is configured.

## Architecture

Two modules with a hard boundary between them:

- `data.py`: pure pandas. Loads and validates the CSV and computes every number and chart series (`load_sales`, `total_sales`, `total_orders`, `monthly_sales`, `sales_by_category`, `sales_by_region`, `format_currency`). It must never import Streamlit, which is what keeps it unit-testable.
- `app.py`: Streamlit layout only, no calculations. It calls `data.py`, builds the Plotly figures, and renders KPI cards, a monthly trend line, and two horizontal bar charts. The `@st.cache_data` wrapper (`get_sales`) lives here, not in `data.py`.

Contracts that span both files:

- **Error handling.** `load_sales` raises `FileNotFoundError` (missing file) or `ValueError` (missing column, unparsable date, no rows). `app.py` catches exactly those two, shows one `st.error`, and calls `st.stop()`. Messages use a short `folder/file` label on purpose so no machine path leaks on a public deploy. Don't widen the `except`.
- **`data.py` vs the `data/` folder.** The module shares its name with the CSV folder. It works because a `.py` module beats a directory without `__init__.py`. Never add `data/__init__.py`. `DEFAULT_PATH` resolves relative to `data.py` (not the working directory) so it also works on Streamlit Cloud.
- **Charts.** Charts are drawn with `st.plotly_chart(..., width="stretch")`, the form verified on Streamlit 1.64 (the `>=` pins in `requirements.txt` are the versions this was built and tested on). Bar charts keep the highest bar on top through `categoryorder="total ascending"` on the y-axis, while the data itself is sorted highest-first. The trend is monthly (12 points), and Total Sales displays in whole dollars.

## Testing

Only `data.py` is unit-tested (`tests/test_data.py`, tiny hand-built DataFrames via `make_sales`, plus one real-data test asserting 482 orders and about $116,500). Write the test first for `data.py` changes. Chart and layout code is deliberately not unit-tested; check it by running the app.

To smoke-check the page without a browser, run it through `streamlit.testing.v1.AppTest.from_file("app.py").run()` and assert on `at.metric`, `at.error`, and `at.get("plotly_chart")`. To inspect a chart's contents, read `json.loads(chart.proto.spec)`. This Plotly version sends numbers as base64 typed arrays (`{"dtype", "bdata"}`), so decode them with `numpy.frombuffer` rather than indexing.

## Environment

- The machine's default `python3` is 3.15.0rc1, on which `pyarrow` (and so Streamlit) does not install. Use a stable 3.11 to 3.13. A checksum-verified standalone 3.12 is at `~/.local/python-3.12-standalone/`.
- Plain `venv/` plus a single `requirements.txt` only. Never add `uv.lock`, `Pipfile`, or `pyproject.toml`: Streamlit Cloud reads those before `requirements.txt` and can break the deploy.

## Workflow rules

- `TASKS.md` is the milestone board (TASK-1 to TASK-6). Every implementation commit message starts with its milestone ID (`TASK-3: ...`).
- After each milestone, record it on the board in its own commit `TASK-N: mark done on the board`. Put the last *code* commit hash on the Commit line and add a Notes line (what needed a human, or "clean"), then move it to Done. The plan's tasks (P1 to P11) have their own numbering; don't confuse them with TASK IDs.
- Work happens on `feature/sales-dashboard` and reaches `main` only by a reviewed merge commit (`--no-ff`). Ask before merging or pushing `main`.
- Deployment (TASK-6) is the owner's manual step on Streamlit Community Cloud, run from `main`. Never deploy it yourself.

## Lessons

Rules distilled from the Notes lines on `TASKS.md`, each one a mistake or near-miss from this build.

- **Prove the interpreter can install the dependencies before building on it.** "Python 3.11+" was satisfied by a 3.15.0rc1 release candidate that still couldn't install Streamlit (no `pyarrow` build). Check first with `pip install --dry-run --only-binary=:all: streamlit pandas plotly pytest` in a scratch venv. (TASK-1)
- **Never put a machine path in a user-facing message.** The first missing-file error printed the full local path twice, and it would have exposed server paths on the public deploy. Use the short `folder/file` label from the start. (TASK-1, fixed in TASK-5)
- **A check that only counts charts proves nothing about them.** Decode the figure (`json.loads(chart.proto.spec)`) and check point counts, that values sum to the overall total ($116,500.21), and the labels and tooltip formats. (TASK-3, TASK-4)
- **Headless checks can't confirm how a chart looks.** Sort order on screen, such as the highest bar on top, goes on the owner's by-eye checklist, and is not reported as verified. (TASK-4)
- **Make sure a verification step can actually detect what it claims to.** `curl` fetches only the HTML shell and never runs the app script, so it can't surface warnings; record warnings during a real `AppTest` run instead. (TASK-5)

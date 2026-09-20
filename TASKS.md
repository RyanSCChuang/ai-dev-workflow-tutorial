# Sales Dashboard: Tasks

This file tracks all work for the e-commerce sales dashboard.
Each milestone moves through To Do -> In Progress -> Done.

## Definition of Done (must hold before any milestone moves to Done)
- Acceptance criteria met
- App runs locally with `streamlit run app.py`
- Changes committed with the milestone ID in the message

## To Do
## In Progress

## Done
- [x] **TASK-1: Project setup and data loading** (PRD M1, M2; FR-5)
  - [x] App runs with `streamlit run app.py` and shows a title
  - [x] Loads `data/sales-data.csv` (date, numeric, and categorical columns); handles a missing file cleanly
  - Commit: 63d7c31
  - Notes: default Python 3.15.0rc1 can't install Streamlit (no pyarrow build), so the venv uses a verified standalone Python 3.12; `data.py` shares a name with the `data/` folder (works, a module beats a folder without `__init__.py`); missing-file error shows the path twice (left as planned, polish in TASK-5)
- [x] **TASK-2: KPI scorecards** (PRD M3; FR-1)
  - [x] Total Sales and Total Orders shown prominently, with currency ($X,XXX,XXX) and thousands separators
  - Commit: 678021e
  - Notes: clean
- [x] **TASK-3: Sales trend chart** (PRD M4; FR-2)
  - [x] Line chart of sales over time (daily or monthly) with correct data and interactive tooltips
  - Commit: a2d3229
  - Notes: clean; the plan's smoke check only counted charts, so I also decoded the figure and confirmed 12 monthly points that sum to $116,500.21
- [x] **TASK-4: Category and region breakdowns** (PRD M5; FR-3, FR-4)
  - [x] Bar chart of sales by category, all 5 categories, sorted highest to lowest, with tooltips
  - [x] Bar chart of sales by region, all 4 regions, sorted highest to lowest, with tooltips
  - Commit: 51cc4d0
  - Notes: clean; decoded both figures (5 and 4 bars, each sums to $116,500.21, dollar tooltips); "highest bar on top" depends on Plotly's axis-order setting and can only be confirmed by eye, which is TASK-5's walk-through
- [x] **TASK-5: Testing and refinement** (PRD M6; Acceptance Criteria, NFR-1, NFR-2)
  - [x] Values match the CSV: about $116,500 total sales and 482 orders
  - [x] Dashboard runs without errors or warnings, with clear labels and a professional appearance
  - Commit: 2483d48
  - Notes: 15 tests pass (real-data test matches the PRD); page loads in 0.41 s; 0 warnings recorded; owner confirmed by eye the KPIs, 3 charts, Electronics and North on top, dollar tooltips, no error box, and a second browser; my plan's curl-based warning check can't run the app, so I recorded warnings during a real run instead; trimmed the doubled machine path from the error message (test first) so a public deploy shows only data/sales-data.csv
- [x] **TASK-6: Deploy to Streamlit Community Cloud** (PRD M7; NFR-5) (human-executed, from `main` after the merge)
  - [x] Deployed from the `main` branch and reachable at a public URL
  - [x] Live URL recorded here and near the top of README.md
  - Commit: c47da9b
  - Live URL: https://sales-dashboard-ryanchuang.streamlit.app/
  - Notes: deployed by the owner by hand from `main` at the merge commit c47da9b (the agent never deployed); an anonymous visitor reaches the app with no sign-in page (checked with a cookie jar, after my first check wrongly suggested a login wall because it dropped cookies); my headless checks can't render the live page, so the charts on the live URL are for the owner to confirm in a browser

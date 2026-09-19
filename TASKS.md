# Sales Dashboard: Tasks

This file tracks all work for the e-commerce sales dashboard.
Each milestone moves through To Do -> In Progress -> Done.

## Definition of Done (must hold before any milestone moves to Done)
- Acceptance criteria met
- App runs locally with `streamlit run app.py`
- Changes committed with the milestone ID in the message

## To Do
- [ ] **TASK-1: Project setup and data loading** (PRD M1, M2; FR-5)
  - [ ] App runs with `streamlit run app.py` and shows a title
  - [ ] Loads `data/sales-data.csv` (date, numeric, and categorical columns); handles a missing file cleanly
  - Commit:
- [ ] **TASK-2: KPI scorecards** (PRD M3; FR-1)
  - [ ] Total Sales and Total Orders shown prominently, with currency ($X,XXX,XXX) and thousands separators
  - Commit:
- [ ] **TASK-3: Sales trend chart** (PRD M4; FR-2)
  - [ ] Line chart of sales over time (daily or monthly) with correct data and interactive tooltips
  - Commit:
- [ ] **TASK-4: Category and region breakdowns** (PRD M5; FR-3, FR-4)
  - [ ] Bar chart of sales by category, all 5 categories, sorted highest to lowest, with tooltips
  - [ ] Bar chart of sales by region, all 4 regions, sorted highest to lowest, with tooltips
  - Commit:
- [ ] **TASK-5: Testing and refinement** (PRD M6; Acceptance Criteria, NFR-1, NFR-2)
  - [ ] Values match the CSV: about $116,500 total sales and 482 orders
  - [ ] Dashboard runs without errors or warnings, with clear labels and a professional appearance
  - Commit:
- [ ] **TASK-6: Deploy to Streamlit Community Cloud** (PRD M7; NFR-5) (human-executed, from `main` after the merge)
  - [ ] Deployed from the `main` branch and reachable at a public URL
  - [ ] Live URL recorded here and near the top of README.md
  - Commit:

## In Progress

## Done

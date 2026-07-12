# 📊 Project Performance Analytics Dashboard
### A combined Project Management + Data Analytics case study — built for the Google Apprenticeship (India) application

---

## 1. The Business Problem

A software company runs 300+ projects at a time across 7 departments. Leadership has no single source of truth to answer:

- Which projects are on track, delayed, or at risk?
- Which teams and managers consistently deliver on time?
- Where is budget being wasted?
- Which projects need executive attention **right now**?

This project solves that — end to end, the way a Project Management + Data Analytics apprentice at Google would be expected to: define the problem, clean the data, analyze it, and ship a decision-ready dashboard.

## 2. What This Repo Contains

| Folder | Contents |
|---|---|
| `data/` | Raw + cleaned datasets (Project & Task tables, ~300 projects / ~9,650 tasks) |
| `scripts/` | Python pipeline: data generation → cleaning → KPIs → charts → Excel build |
| `sql/` | 10 business-question SQL queries, tested against SQLite |
| `excel/` | Interactive Excel dashboard (formulas, not hardcoded values) |
| `powerbi/` | Power BI build guide + DAX measures (data model, pages, slicers) |
| `outputs/` | Generated charts (13) + KPI summary (JSON) |
| `presentation/` | 12-slide stakeholder presentation |
| `docs/` | Full project documentation, resume bullets, LinkedIn post, interview Q&A |

## 3. The Datasets

Two datasets, linked by `Project_ID`, mimicking how real companies store this data across a PM tool (Jira/Asana) and an HR/timesheet system:

**`project_data.csv`** (300 rows) — Project ID, Name, Manager, Team, Department, Start/End/Planned dates, Status, Priority, Budget, Actual Cost, Progress %, Risk Level, Client, Team Size

**`task_data.csv`** (~9,650 rows) — Task ID, Project ID, Employee, Task Name, Assigned/Due/Completed dates, Hours Worked, Estimated Hours, Task Status, Priority, Type, Bug Count, Rework Hours

Both include realistic messiness (missing values, duplicates) that gets cleaned as part of the pipeline — because real company data is never clean.

## 4. Pipeline — How to Run It

```bash
pip install pandas numpy matplotlib seaborn openpyxl

python scripts/01_generate_data.py          # generate raw datasets
python scripts/02_clean_and_merge.py        # clean, dedupe, merge
python scripts/03_kpi_and_charts.py         # compute KPIs, generate 13 charts
python scripts/04_build_excel_dashboard.py  # build the Excel dashboard
```

SQL queries can be run against `data/project_analytics.db` (SQLite) or loaded into any RDBMS using `sql/queries.sql`.

## 5. Key KPIs Delivered

Total Projects · Completed / Delayed / In Progress · Average Completion % · Budget Utilization % · Cost Overrun · Average Delay Days · Project Success Rate · Task Completion Rate · Employee Productivity · Risk Distribution · Top Teams/Managers · Highest-Cost & Most-Delayed Projects

## 6. Headline Insights

- **63.8% project success rate** — over a third of projects miss their planned end date.
- Delayed projects run **18 days late on average**, and cost **~9% more** than their budget.
- Departments with the highest **risk concentration** also show the highest **cost overruns** — risk and budget are not being managed together today.
- A small group of teams and managers consistently outperform the rest — their practices are a template worth replicating.

Full breakdown in [`docs/documentation.md`](docs/documentation.md).

## 7. Tools Used

Python (Pandas, NumPy, Matplotlib, Seaborn) · SQL (SQLite) · Excel (openpyxl, formulas + charts) · Power BI (DAX, data model) · Git/GitHub

## 8. Author

Built by [Your Name], BCA student, as a portfolio project for the Google Apprenticeship Program (India).

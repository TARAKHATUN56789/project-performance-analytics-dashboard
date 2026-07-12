# Project Documentation — Project Performance Analytics Dashboard

## 1. Objective
Build a single, decision-ready analytics system that lets management see, in one place: which projects are healthy, which are at risk, where money is being wasted, and who is performing well — combining the discipline of **project management** with the rigor of **data analytics**.

## 2. Data Sources & Structure

| Dataset | Rows | Grain | Key |
|---|---|---|---|
| Project Data | 300 | 1 row per project | `Project_ID` |
| Task Data | ~9,650 | 1 row per task | `Task_ID`, FK `Project_ID` |

The two tables are related **one-to-many**: each project has 20–45 tasks, worked on by employees across a shared pool of ~600 staff.

## 3. Data Cleaning (Step-by-Step)

1. **Deduplication** — 6 duplicate project rows and 25 duplicate task rows removed using `drop_duplicates()` on the primary key.
2. **Missing values**:
   - `Risk_Level` (0.7% missing) → filled as `"Not Assessed"` rather than dropped, since a missing risk rating is itself meaningful information for the risk team.
   - `Team_Size` (~3% missing) → filled with the **department median** (more accurate than a global average, since team sizes vary structurally by department).
   - `Hours_Worked` (~2% missing) → filled with `0`, since a missing value here means no time had been logged yet.
3. **Type correction** — all date columns converted from text to proper `datetime`.
4. **Feature engineering**:
   - `Delay_Days` = actual/current date − planned end date (floored at 0)
   - `Cost_Variance` / `Cost_Variance_%` = actual cost vs. budget
   - `Is_Delayed`, `Is_Over_Budget` — boolean flags for fast filtering
   - `Is_Late` (task-level) — whether a task finished after its due date
   - `Efficiency_Ratio` = estimated hours ÷ actual hours worked

## 4. Exploratory Data Analysis — What We Looked At

- Distribution of project status, priority, and risk level
- Budget vs. actual cost by department
- Delay patterns by department, team, priority, and risk level
- Task completion trends over time
- Employee-level productivity (tasks completed, hours logged, bug/rework rates)

## 5. Key Findings

| Metric | Value |
|---|---|
| Total Projects | 300 |
| Completed | 190 (63.3%) |
| Delayed | 108 (36%) |
| Project Success Rate | **63.76%** |
| Average Delay (delayed projects) | **18 days** |
| Total Budget | ₹3.57 Cr |
| Total Actual Cost | ₹3.78 Cr |
| Budget Utilization | **105.95%** (over budget) |
| Projects Over Budget | 153 (51%) |
| Task Completion Rate | 88.46% |
| Avg. Tasks per Employee | 29.26 |

**Risk distribution:** Medium (113) ≈ Low (111) > High (68) > Not Assessed (8) — over a fifth of all projects carry high risk.

**Top performing teams (by success rate):** Nova (82.9%), Comet (75%), Quantum (75%)
**Top performing managers:** Sneha Reddy (81%), Ananya Rao (71.4%), Neha Kapoor (69.7%)

## 6. Answers to the Business Questions

1. **Which projects are delayed and why?** 108 projects (36%) — concentrated in High-Risk, High/Critical-Priority projects, which show the longest average delays (see `sql/queries.sql` Q1, Q7).
2. **Which manager delivers on time most often?** Sneha Reddy, at an 81% success rate across her portfolio.
3. **Which departments exceed budget?** 7 of 7 departments show at least some overrun; AI/ML and Cloud Infrastructure show the largest absolute overruns due to higher per-project cost.
4. **Which projects have the highest risk?** 68 projects flagged High risk — cross-referencing with delay and cost data identifies which need the most urgent attention (Q9).
5. **Which teams complete tasks fastest?** Teams with the highest on-time task completion rate are identified in Q5 — these show visibly tighter turnaround between assignment and completion.
6. **Which employees are most productive?** Ranked by tasks completed and hours efficiency in Q6 — the top 15 combine high task volume with low rework hours.
7. **What causes delays?** High risk + High/Critical priority is the strongest combination associated with long delays — larger teams do not reliably fix this.
8. **How can costs be reduced?** The departments/project types with the highest average cost variance % point to where estimation practices need the most improvement (Q8).
9. **Which projects need immediate attention?** Projects that are simultaneously High Risk + Delayed + Over Budget — a small, clearly identifiable list (Q9) that should be the first stop for management.

## 7. Recommendations

1. **Triage the "triple red flag" list** (high risk + delayed + over budget) first — it's a small list with outsized impact.
2. **Standardize the practices of top-performing teams/managers** (Nova, Sneha Reddy) — investigate what makes their delivery more reliable and pilot it in underperforming teams.
3. **Tighten estimation for High/Critical priority projects** — these show the largest average delay and cost variance, suggesting planning is too optimistic at the point of approval.
4. **Formalize risk assessment** — 8 projects have no risk rating at all; an unassessed project is a blind spot, not a safe one.
5. **Set a budget utilization alert at 100%** — over half of all projects (51%) are already over budget by the time this dashboard would flag them; earlier warning thresholds (e.g., at 85% utilization with <70% progress) would catch this sooner.

## 8. Tools & Technical Stack

- **Python** (Pandas, NumPy) — data cleaning, merging, feature engineering
- **Matplotlib / Seaborn** — 13 analytical charts
- **SQL (SQLite)** — 10 business-question queries, portable to MySQL/PostgreSQL
- **Excel (openpyxl)** — interactive dashboard with live formulas (COUNTIFS/SUMIF-driven), zero formula errors
- **Power BI** — interactive multi-page dashboard (see `powerbi/POWERBI_GUIDE.md`)
- **Git/GitHub** — version-controlled, portfolio-ready repo structure

## 9. Limitations & Next Steps

- Data is synthetically generated to resemble real company patterns (not from an actual company) — this is disclosed transparently in interviews.
- Next iteration: add a live "days to attention" alerting logic and connect it to a mock Slack/email notification for high-risk projects.

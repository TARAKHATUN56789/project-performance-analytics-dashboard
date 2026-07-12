# Power BI Dashboard — Build Guide

> **Note on scope:** Power BI Desktop isn't available in this environment, so this is a precise, ready-to-follow build spec (data model, DAX measures, page layout, and interactivity) rather than a pre-made `.pbix` file. Following the steps below in Power BI Desktop (free) will take ~1-2 hours and produce exactly the dashboard described. Use `data/project_data_clean.csv` and `data/task_data_clean.csv` as your two data sources.

## 1. Data Model

1. **Get Data → Text/CSV** → import both `project_data_clean.csv` and `task_data_clean.csv`.
2. Go to **Model view** and create a relationship:
   - `projects[Project_ID]` (1) → `tasks[Project_ID]` (many)
3. Create a **Date table** (Modeling → New Table):
   ```
   DateTable = CALENDAR(DATE(2023,1,1), DATE(2026,12,31))
   ```
   Mark it as a Date Table (Modeling → Mark as Date Table), and relate `DateTable[Date]` to `projects[Start_Date]`.

## 2. Core DAX Measures

Paste these into a new measures table (`_Measures`):

```DAX
Total Projects = COUNTROWS(projects)

Completed Projects = CALCULATE(COUNTROWS(projects), projects[Status] = "Completed")

Delayed Projects = CALCULATE(COUNTROWS(projects), projects[Status] = "Delayed")

Project Success Rate % =
DIVIDE([Completed Projects], [Completed Projects] + [Delayed Projects], 0)

Average Completion % = AVERAGE(projects[Progress_%])

Total Budget = SUM(projects[Budget])

Total Actual Cost = SUM(projects[Actual_Cost])

Budget Utilization % = DIVIDE([Total Actual Cost], [Total Budget], 0)

Cost Overrun = SUMX(projects, MAX(projects[Actual_Cost] - projects[Budget], 0))

Projects Over Budget = CALCULATE(COUNTROWS(projects), projects[Actual_Cost] > projects[Budget])

Average Delay Days =
CALCULATE(AVERAGE(projects[Delay_Days]), projects[Status] IN {"Completed","Delayed"})

Task Completion Rate % =
DIVIDE(CALCULATE(COUNTROWS(tasks), tasks[Task_Status] = "Completed"), COUNTROWS(tasks), 0)

Avg Tasks per Employee =
DIVIDE(COUNTROWS(tasks), DISTINCTCOUNT(tasks[Employee_ID]), 0)

High Risk Projects = CALCULATE(COUNTROWS(projects), projects[Risk_Level] = "High")

Needs Immediate Attention =
CALCULATE(
    COUNTROWS(projects),
    projects[Risk_Level] = "High",
    projects[Status] = "Delayed",
    projects[Actual_Cost] > projects[Budget]
)
```

## 3. Pages & Layout

### Page 1 — Executive Overview
- **KPI Cards** (top row): Total Projects, Success Rate %, Budget Utilization %, Delayed Projects, Needs Immediate Attention
- **Donut chart**: Project Status
- **Bar chart**: Budget vs Actual Cost by Department
- **Line chart**: Monthly Project Completion Trend
- **Slicers** (right-hand panel): Department, Priority, Risk Level, Date range

### Page 2 — Project Manager View
- **Table**: Project_ID, Name, Manager, Status, Delay Days, Risk Level, Cost Variance % (conditional formatting: red for over budget/high risk)
- **Gantt-style chart** (use a Gantt custom visual, or a stacked bar with Start Date + Duration): sample of active projects
- **Risk Heatmap** (matrix visual): Department × Risk Level, values = project count, conditional formatting
- **Slicers**: Project Manager, Team

### Page 3 — Employee & Task Performance
- **Bar chart**: Top 15 Employees by Tasks Completed
- **Line chart**: Monthly Task Completion Trend
- **Scatter chart**: Estimated Hours vs Hours Worked (bubble size = Bug Count) — flags over/under-estimated tasks
- **Table**: Employee productivity summary (tasks completed, hours, efficiency ratio)

### Page 4 — Drill-Through: Project Detail
- Right-click any project on Page 1/2 → **Drill through** to this page
- Shows: full project record, its task list, cost trend, and a text box with auto-generated status commentary

## 4. Interactivity Checklist

- [ ] Slicers for Department, Priority, Risk Level, Project Manager, Date range
- [ ] Cross-filtering enabled between all visuals on a page
- [ ] Drill-through page configured (Page 1/2 → Page 4, passing Project_ID)
- [ ] Navigation buttons (Insert → Buttons → Blank) linking all 4 pages, styled consistently
- [ ] Bookmarks for "Executive View" vs "Detailed View" toggle (optional polish)

## 5. Google-Style Color Theme

Use **View → Themes → Customize current theme**:
- Primary: `#4285F4` (Google Blue)
- Positive/Success: `#34A853` (Google Green)
- Warning/Risk: `#FBBC05` (Google Yellow)
- Negative/Delay: `#EA4335` (Google Red)
- Background: `#FFFFFF`, Text: `#202124`

## 6. Publishing Note

Once built, publish to Power BI Service and add the shareable link to your README/LinkedIn post — recruiters can open it directly without needing Power BI installed.

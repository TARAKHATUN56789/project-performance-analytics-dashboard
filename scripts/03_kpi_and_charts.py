"""
03_kpi_and_charts.py
---------------------
Step 2 of the pipeline: calculate every KPI requested for the dashboard
and generate all the charts (saved as PNGs) that would sit inside the
Power BI / Excel dashboards and the presentation deck.

Run:
    python 03_kpi_and_charts.py
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import json

DATA_DIR = "../data"
CHART_DIR = "../outputs/charts"

sns.set_theme(style="whitegrid")
GOOGLE_COLORS = ["#4285F4", "#EA4335", "#FBBC05", "#34A853", "#5F6368"]
sns.set_palette(GOOGLE_COLORS)
plt.rcParams["figure.dpi"] = 130
plt.rcParams["font.size"] = 10

projects = pd.read_csv(f"{DATA_DIR}/project_data_clean.csv", parse_dates=["Start_Date", "End_Date", "Planned_End_Date"])
tasks = pd.read_csv(f"{DATA_DIR}/task_data_clean.csv", parse_dates=["Assigned_Date", "Due_Date", "Completed_Date"])
merged = pd.read_csv(f"{DATA_DIR}/merged_master.csv")

# ===========================================================================
# PART A — KPI CALCULATIONS
# ===========================================================================
kpis = {}

kpis["Total_Projects"] = int(projects.shape[0])
kpis["Completed_Projects"] = int((projects["Status"] == "Completed").sum())
kpis["Delayed_Projects"] = int((projects["Status"] == "Delayed").sum())
kpis["In_Progress_Projects"] = int((projects["Status"] == "In Progress").sum())

kpis["Average_Completion_%"] = round(projects["Progress_%"].mean(), 2)

kpis["Total_Budget"] = round(projects["Budget"].sum(), 2)
kpis["Total_Actual_Cost"] = round(projects["Actual_Cost"].sum(), 2)
kpis["Budget_Utilization_%"] = round(kpis["Total_Actual_Cost"] / kpis["Total_Budget"] * 100, 2)
kpis["Cost_Overrun_Total"] = round((projects["Actual_Cost"] - projects["Budget"]).clip(lower=0).sum(), 2)
kpis["Projects_Over_Budget"] = int((projects["Actual_Cost"] > projects["Budget"]).sum())

finished = projects[projects["Status"].isin(["Completed", "Delayed"])]
kpis["Average_Delay_Days"] = round(finished["Delay_Days"].mean(), 1)

kpis["Project_Success_Rate_%"] = round(
    kpis["Completed_Projects"] / (kpis["Completed_Projects"] + kpis["Delayed_Projects"]) * 100, 2
)

kpis["Task_Completion_Rate_%"] = round((tasks["Task_Status"] == "Completed").mean() * 100, 2)

emp_hours = tasks.groupby("Employee_Name")["Hours_Worked"].sum()
emp_tasks = tasks.groupby("Employee_Name")["Task_ID"].count()
kpis["Average_Employee_Productivity_(tasks_per_employee)"] = round(emp_tasks.mean(), 2)

risk_dist = projects["Risk_Level"].value_counts().to_dict()
kpis["Risk_Distribution"] = risk_dist

team_success = projects.groupby("Team_Name").apply(
    lambda x: round((x["Status"] == "Completed").mean() * 100, 1)
).sort_values(ascending=False)
kpis["Top_3_Performing_Teams"] = team_success.head(3).to_dict()

mgr_success = projects.groupby("Project_Manager").apply(
    lambda x: round((x["Status"] == "Completed").mean() * 100, 1)
).sort_values(ascending=False)
kpis["Top_3_Performing_Managers"] = mgr_success.head(3).to_dict()

kpis["Top_5_Highest_Cost_Projects"] = projects.nlargest(5, "Actual_Cost")[
    ["Project_ID", "Project_Name", "Actual_Cost"]].to_dict("records")

kpis["Top_5_Most_Delayed_Projects"] = projects.nlargest(5, "Delay_Days")[
    ["Project_ID", "Project_Name", "Delay_Days"]].to_dict("records")

with open("../outputs/kpi_summary.json", "w") as f:
    json.dump(kpis, f, indent=2, default=str)

print("KPI SUMMARY")
for k, v in kpis.items():
    if not isinstance(v, (dict, list)):
        print(f"  {k}: {v}")

# ===========================================================================
# PART B — CHARTS  (13 charts total)
# ===========================================================================

# 1. Project Status (donut)
plt.figure(figsize=(6, 6))
status_counts = projects["Status"].value_counts()
plt.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%",
        colors=GOOGLE_COLORS, wedgeprops=dict(width=0.4, edgecolor="white"))
plt.title("Project Status Distribution")
plt.savefig(f"{CHART_DIR}/01_project_status.png", bbox_inches="tight")
plt.close()

# 2. Monthly Project Completion (line)
completed = projects[projects["Status"] == "Completed"].copy()
completed["Month"] = completed["End_Date"].dt.to_period("M").astype(str)
monthly = completed.groupby("Month").size().reset_index(name="Completed")
plt.figure(figsize=(10, 5))
plt.plot(monthly["Month"], monthly["Completed"], marker="o", color=GOOGLE_COLORS[0])
plt.xticks(rotation=75, fontsize=7)
plt.title("Monthly Project Completion Trend")
plt.ylabel("Projects Completed")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/02_monthly_completion.png")
plt.close()

# 3. Budget vs Actual Cost (grouped bar, by department)
dept_cost = projects.groupby("Department")[["Budget", "Actual_Cost"]].sum().sort_values("Budget", ascending=False)
dept_cost.plot(kind="bar", figsize=(10, 5), color=[GOOGLE_COLORS[0], GOOGLE_COLORS[1]])
plt.title("Budget vs Actual Cost by Department")
plt.ylabel("Amount (₹)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/03_budget_vs_actual.png")
plt.close()

# 4. Timeline (Gantt-style) for a sample of 15 projects
sample = projects.sample(15, random_state=1).sort_values("Start_Date")
fig, ax = plt.subplots(figsize=(10, 6))
for i, row in enumerate(sample.itertuples()):
    end = row.End_Date if pd.notna(row.End_Date) else row.Planned_End_Date
    ax.barh(i, (pd.Timestamp(end) - row.Start_Date).days, left=row.Start_Date,
            color=GOOGLE_COLORS[0] if row.Status == "Completed" else
            (GOOGLE_COLORS[1] if row.Status == "Delayed" else GOOGLE_COLORS[2]))
ax.set_yticks(range(len(sample)))
ax.set_yticklabels(sample["Project_ID"])
ax.set_title("Project Timeline (Gantt-style sample of 15 projects)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/04_gantt_timeline.png")
plt.close()

# 5. Project Progress % distribution (histogram)
plt.figure(figsize=(8, 5))
plt.hist(projects["Progress_%"], bins=20, color=GOOGLE_COLORS[3], edgecolor="white")
plt.title("Distribution of Project Progress %")
plt.xlabel("Progress %")
plt.ylabel("Number of Projects")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/05_progress_distribution.png")
plt.close()

# 6. Risk Heatmap (Department x Risk Level)
risk_pivot = pd.crosstab(projects["Department"], projects["Risk_Level"])
plt.figure(figsize=(8, 6))
sns.heatmap(risk_pivot, annot=True, fmt="d", cmap="Reds")
plt.title("Risk Heatmap: Department vs Risk Level")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/06_risk_heatmap.png")
plt.close()

# 7. Employee Productivity (top 15 by tasks completed)
top_emp = tasks[tasks["Task_Status"] == "Completed"].groupby("Employee_Name").size() \
    .sort_values(ascending=False).head(15)
plt.figure(figsize=(9, 6))
top_emp.sort_values().plot(kind="barh", color=GOOGLE_COLORS[0])
plt.title("Top 15 Employees by Tasks Completed")
plt.xlabel("Tasks Completed")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/07_employee_productivity.png")
plt.close()

# 8. Task Completion Trend (monthly)
tasks_completed = tasks[tasks["Completed_Date"].notna()].copy()
tasks_completed["Month"] = tasks_completed["Completed_Date"].dt.to_period("M").astype(str)
task_trend = tasks_completed.groupby("Month").size().reset_index(name="Completed_Tasks")
plt.figure(figsize=(10, 5))
plt.plot(task_trend["Month"], task_trend["Completed_Tasks"], marker="o", color=GOOGLE_COLORS[3])
plt.xticks(rotation=75, fontsize=7)
plt.title("Monthly Task Completion Trend")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/08_task_completion_trend.png")
plt.close()

# 9. Department Performance (success rate)
dept_success = projects.groupby("Department").apply(lambda x: (x["Status"] == "Completed").mean() * 100) \
    .sort_values()
plt.figure(figsize=(8, 6))
dept_success.plot(kind="barh", color=GOOGLE_COLORS[2])
plt.title("Department Performance (Success Rate %)")
plt.xlabel("Success Rate %")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/09_department_performance.png")
plt.close()

# 10. Manager Performance (top 10)
plt.figure(figsize=(8, 6))
mgr_success.head(10).sort_values().plot(kind="barh", color=GOOGLE_COLORS[0])
plt.title("Top 10 Project Managers by Success Rate %")
plt.xlabel("Success Rate %")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/10_manager_performance.png")
plt.close()

# 11. Priority Distribution
plt.figure(figsize=(6, 6))
priority_counts = projects["Priority"].value_counts()
plt.pie(priority_counts, labels=priority_counts.index, autopct="%1.1f%%", colors=GOOGLE_COLORS)
plt.title("Project Priority Distribution")
plt.savefig(f"{CHART_DIR}/11_priority_distribution.png")
plt.close()

# 12. Delay Analysis (delay days by department, boxplot)
plt.figure(figsize=(9, 6))
sns.boxplot(data=finished, x="Department", y="Delay_Days", palette=GOOGLE_COLORS)
plt.xticks(rotation=30, ha="right")
plt.title("Delay Analysis by Department")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/12_delay_analysis.png")
plt.close()

# 13. Cost Analysis (cost variance % distribution)
plt.figure(figsize=(8, 5))
plt.hist(projects["Cost_Variance_%"], bins=25, color=GOOGLE_COLORS[1], edgecolor="white")
plt.axvline(0, color="black", linestyle="--", linewidth=1)
plt.title("Cost Variance % Distribution (Actual vs Budget)")
plt.xlabel("Cost Variance %")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/13_cost_analysis.png")
plt.close()

print("\nAll 13 charts saved to:", CHART_DIR)

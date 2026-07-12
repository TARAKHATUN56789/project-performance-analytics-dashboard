"""
02_clean_and_merge.py
----------------------
Step 1 of the analysis pipeline: clean both raw datasets and merge them
into a single analysis-ready table.

What this script does (in plain English, so you can explain it in an
interview):
  1. Loads both CSVs.
  2. Removes exact duplicate rows (Project_ID / Task_ID level).
  3. Handles missing values sensibly (not just dropping rows blindly):
       - Missing Risk_Level  -> filled with "Not Assessed"
       - Missing Team_Size   -> filled with department median
       - Missing Hours_Worked-> filled with 0 (task hasn't logged time yet)
  4. Converts date columns to proper datetime type.
  5. Merges Task data with Project data using Project_ID (the shared key).
  6. Saves a clean master file used by every later script.
"""

import pandas as pd
import numpy as np

DATA_DIR = "../data"

# ---------------------------------------------------------------------------
# 1. LOAD RAW DATA
# ---------------------------------------------------------------------------
projects = pd.read_csv(f"{DATA_DIR}/project_data.csv")
tasks = pd.read_csv(f"{DATA_DIR}/task_data.csv")

print("RAW SHAPES:", "projects:", projects.shape, "| tasks:", tasks.shape)

# ---------------------------------------------------------------------------
# 2. REMOVE DUPLICATES
# ---------------------------------------------------------------------------
projects_before = projects.shape[0]
projects = projects.drop_duplicates(subset="Project_ID", keep="first")
tasks_before = tasks.shape[0]
tasks = tasks.drop_duplicates(subset="Task_ID", keep="first")

print(f"Removed {projects_before - projects.shape[0]} duplicate project rows")
print(f"Removed {tasks_before - tasks.shape[0]} duplicate task rows")

# ---------------------------------------------------------------------------
# 3. HANDLE MISSING VALUES
# ---------------------------------------------------------------------------
# Risk_Level: unknown risk shouldn't be silently dropped -> label it clearly
projects["Risk_Level"] = projects["Risk_Level"].fillna("Not Assessed")

# Team_Size: fill with the median team size for that department (more accurate
# than a global average, since departments differ in typical team size)
projects["Team_Size"] = projects.groupby("Department")["Team_Size"] \
    .transform(lambda x: x.fillna(x.median()))
projects["Team_Size"] = projects["Team_Size"].round().astype(int)

# Hours_Worked in tasks: missing means effectively no time logged yet
tasks["Hours_Worked"] = tasks["Hours_Worked"].fillna(0)

# ---------------------------------------------------------------------------
# 4. FIX DATA TYPES (dates)
# ---------------------------------------------------------------------------
date_cols_proj = ["Start_Date", "End_Date", "Planned_End_Date"]
for c in date_cols_proj:
    projects[c] = pd.to_datetime(projects[c], errors="coerce")

date_cols_task = ["Assigned_Date", "Due_Date", "Completed_Date"]
for c in date_cols_task:
    tasks[c] = pd.to_datetime(tasks[c], errors="coerce")

# ---------------------------------------------------------------------------
# 5. DERIVED / ENGINEERED COLUMNS (used heavily in later analysis)
# ---------------------------------------------------------------------------
# Project-level: delay days (positive = late), budget variance
projects["Delay_Days"] = (projects["End_Date"].fillna(pd.Timestamp("2025-12-31"))
                           - projects["Planned_End_Date"]).dt.days
projects["Delay_Days"] = projects["Delay_Days"].clip(lower=0)

projects["Cost_Variance"] = projects["Actual_Cost"] - projects["Budget"]
projects["Cost_Variance_%"] = (projects["Cost_Variance"] / projects["Budget"] * 100).round(2)
projects["Is_Delayed"] = projects["Status"] == "Delayed"
projects["Is_Over_Budget"] = projects["Actual_Cost"] > projects["Budget"]

# Task-level: was the task completed late? task efficiency (est vs actual hours)
tasks["Is_Completed"] = tasks["Task_Status"] == "Completed"
tasks["Is_Late"] = np.where(
    tasks["Completed_Date"].notna() & tasks["Due_Date"].notna(),
    tasks["Completed_Date"] > tasks["Due_Date"],
    False
)
tasks["Hours_Variance"] = tasks["Hours_Worked"] - tasks["Estimated_Hours"]
tasks["Efficiency_Ratio"] = (tasks["Estimated_Hours"] / tasks["Hours_Worked"].replace(0, np.nan)).round(2)

# ---------------------------------------------------------------------------
# 6. MERGE (Task Performance + Project Management) ON Project_ID
# ---------------------------------------------------------------------------
merged = tasks.merge(projects, on="Project_ID", how="left", suffixes=("_task", "_proj"))

print("CLEAN SHAPES:", "projects:", projects.shape, "| tasks:", tasks.shape,
      "| merged:", merged.shape)

# ---------------------------------------------------------------------------
# 7. SAVE CLEAN OUTPUTS
# ---------------------------------------------------------------------------
projects.to_csv(f"{DATA_DIR}/project_data_clean.csv", index=False)
tasks.to_csv(f"{DATA_DIR}/task_data_clean.csv", index=False)
merged.to_csv(f"{DATA_DIR}/merged_master.csv", index=False)

print("Saved: project_data_clean.csv, task_data_clean.csv, merged_master.csv")

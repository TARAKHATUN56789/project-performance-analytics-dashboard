"""
01_generate_data.py

Generates two realistic, connected datasets for the Project Performance
Analytics Dashboard project:

  1. project_data.csv   -> 300 software projects (management-level info)
  2. task_data.csv      -> 9,000 tasks belonging to those projects

Both files are linked by "Project ID", exactly like two tables in a real
company database (this mirrors how PMs and analysts work with data coming
from a Project Management tool (like Jira/Asana) + an HR/timesheet tool).

Run:
    python 01_generate_data.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# Reproducible "randomness" so results are consistent every time we re-run
np.random.seed(42)
random.seed(42)

# ---------------------------------------------------------------------------
# 1. REFERENCE / LOOKUP LISTS
# ---------------------------------------------------------------------------
departments = ["Engineering", "Data & Analytics", "Cloud Infrastructure",
               "Mobile Apps", "AI/ML", "QA & Testing", "Customer Platforms"]

teams = ["Falcon", "Orion", "Nova", "Atlas", "Titan", "Pulsar", "Vega",
         "Zenith", "Quantum", "Nimbus", "Comet", "Aurora"]

managers = ["Ananya Rao", "Rohit Sharma", "Priya Menon", "Karthik Iyer",
            "Sneha Reddy", "Arjun Nair", "Divya Pillai", "Vikram Malhotra",
            "Meera Krishnan", "Suresh Kumar", "Neha Kapoor", "Aditya Verma"]

clients = ["Internal", "Fintech Client A", "Retail Client B", "Healthcare Client C",
           "EdTech Client D", "Logistics Client E", "BFSI Client F", "Govt Client G"]

priorities = ["Low", "Medium", "High", "Critical"]
priority_weights = [0.15, 0.40, 0.30, 0.15]

risk_levels = ["Low", "Medium", "High"]

project_types = ["Web App", "Mobile App", "Data Pipeline", "ML Model",
                  "Cloud Migration", "API Integration", "Internal Tool", "Dashboard"]

employees_pool = [f"EMP{str(i).zfill(4)}" for i in range(1, 601)]  # 600 employees
first_names = ["Aarav","Vivaan","Aditya","Diya","Ishaan","Ananya","Reyansh","Myra",
               "Kabir","Anika","Vihaan","Saanvi","Arnav","Aadhya","Kiaan","Riya",
               "Yuvan","Navya","Aryan","Meera","Dhruv","Sara","Rudra","Zara",
               "Advait","Kavya","Shaurya","Ira","Veer","Tara"]
last_names = ["Sharma","Verma","Iyer","Nair","Reddy","Rao","Menon","Gupta",
              "Kapoor","Malhotra","Kumar","Singh","Pillai","Krishnan","Das","Bose"]

employee_names = {emp: f"{random.choice(first_names)} {random.choice(last_names)}"
                   for emp in employees_pool}

task_types = ["Development", "Testing", "Design", "Documentation",
              "Code Review", "Deployment", "Bug Fix", "Research"]

task_priorities = ["Low", "Medium", "High"]

# ---------------------------------------------------------------------------
# 2. GENERATE PROJECT_DATA (the "Project Management" table)
# ---------------------------------------------------------------------------
N_PROJECTS = 300
project_rows = []
base_date = datetime(2023, 1, 1)

for i in range(1, N_PROJECTS + 1):
    project_id = f"PRJ{str(i).zfill(4)}"
    department = random.choice(departments)
    team = random.choice(teams)
    manager = random.choice(managers)
    client = random.choice(clients)
    priority = np.random.choice(priorities, p=priority_weights)
    ptype = random.choice(project_types)

    # Timeline: random start date within a ~2.5 year window
    start_offset = random.randint(0, 880)
    start_date = base_date + timedelta(days=start_offset)

    planned_duration = random.randint(30, 270)          # planned length in days
    planned_end_date = start_date + timedelta(days=planned_duration)

    team_size = random.randint(3, 15)
    budget = round(random.uniform(5, 120) * 1000 * (team_size / 5), 2)  # scales with team size

    # Decide status based on where planned_end_date falls relative to "today"
    today = datetime(2025, 12, 31)  # snapshot date used as "now" for this dataset

    # Introduce realistic delay behavior: ~38% of projects run late
    is_delayed = random.random() < 0.38
    if planned_end_date > today:
        # Still ongoing
        status = "In Progress"
        end_date = None
        progress_pct = round(random.uniform(10, 90), 1)
    else:
        if is_delayed:
            delay_days = random.randint(5, 90)
            end_date = planned_end_date + timedelta(days=delay_days)
            # "Delayed" = project overran its planned end date (whether it has
            # since finished late, or is still open past its due date)
            status = "Delayed"
            progress_pct = 100.0 if end_date <= today else round(random.uniform(60, 95), 1)
        else:
            end_date = planned_end_date - timedelta(days=random.randint(0, 10))
            status = "Completed"
            progress_pct = 100.0

    # Cost behavior correlates loosely with delay/risk
    if status == "Completed" and not is_delayed:
        actual_cost = round(budget * random.uniform(0.85, 1.05), 2)
    elif is_delayed:
        actual_cost = round(budget * random.uniform(1.05, 1.45), 2)
    else:
        actual_cost = round(budget * random.uniform(0.4, 0.95), 2)  # still in progress, partial spend

    # Risk level correlates with priority + delay
    if is_delayed and priority in ["High", "Critical"]:
        risk_level = np.random.choice(risk_levels, p=[0.10, 0.30, 0.60])
    elif is_delayed:
        risk_level = np.random.choice(risk_levels, p=[0.20, 0.45, 0.35])
    else:
        risk_level = np.random.choice(risk_levels, p=[0.55, 0.35, 0.10])

    # Randomly introduce some messy/missing data (realistic for a portfolio project)
    if random.random() < 0.03:
        team_size_val = None
    else:
        team_size_val = team_size

    if random.random() < 0.02:
        risk_level_val = None
    else:
        risk_level_val = risk_level

    project_rows.append({
        "Project_ID": project_id,
        "Project_Name": f"{ptype} - {client if client != 'Internal' else department} #{i}",
        "Project_Manager": manager,
        "Team_Name": team,
        "Department": department,
        "Project_Type": ptype,
        "Start_Date": start_date.strftime("%Y-%m-%d"),
        "End_Date": end_date.strftime("%Y-%m-%d") if end_date else None,
        "Planned_End_Date": planned_end_date.strftime("%Y-%m-%d"),
        "Status": status,
        "Priority": priority,
        "Budget": budget,
        "Actual_Cost": actual_cost,
        "Progress_%": progress_pct,
        "Risk_Level": risk_level_val,
        "Client": client,
        "Team_Size": team_size_val
    })

# Inject a handful of exact duplicate rows on purpose (to be cleaned later)
for _ in range(6):
    project_rows.append(random.choice(project_rows[:N_PROJECTS]).copy())

project_df = pd.DataFrame(project_rows)
project_df.to_csv("../data/project_data.csv", index=False)
print(f"project_data.csv created -> {project_df.shape[0]} rows, {project_df.shape[1]} columns")

# ---------------------------------------------------------------------------
# 3. GENERATE TASK_DATA (the "Task Performance" table, linked by Project_ID)
# ---------------------------------------------------------------------------
task_rows = []
task_counter = 1

for _, proj in project_df.drop_duplicates(subset="Project_ID").iterrows():
    n_tasks = random.randint(20, 45)  # tasks per project
    proj_start = datetime.strptime(proj["Start_Date"], "%Y-%m-%d")
    end_val = proj["End_Date"]
    proj_end_ref = end_val if isinstance(end_val, str) and end_val else proj["Planned_End_Date"]
    proj_end = datetime.strptime(proj_end_ref, "%Y-%m-%d")
    span_days = max((proj_end - proj_start).days, 10)

    for _ in range(n_tasks):
        task_id = f"TSK{str(task_counter).zfill(6)}"
        task_counter += 1

        employee_id = random.choice(employees_pool)
        assigned_offset = random.randint(0, span_days - 1)
        assigned_date = proj_start + timedelta(days=assigned_offset)
        est_hours = round(random.uniform(4, 60), 1)

        due_date = assigned_date + timedelta(days=random.randint(2, 21))

        # Completion behavior
        completes = random.random() < 0.88  # 12% still open/in-progress
        if completes:
            # Some tasks finish early, some late
            delay = np.random.choice([-2, -1, 0, 1, 2, 3, 5, 8, 12],
                                      p=[0.10, 0.12, 0.20, 0.18, 0.14, 0.10, 0.08, 0.05, 0.03])
            completed_date = due_date + timedelta(days=int(delay))
            task_status = "Completed"
            hours_worked = round(max(est_hours * random.uniform(0.7, 1.6), 1), 1)
        else:
            completed_date = None
            task_status = random.choice(["In Progress", "Blocked", "To Do"])
            hours_worked = round(max(est_hours * random.uniform(0.1, 0.9), 0), 1)

        bug_count = np.random.poisson(1.2) if random.random() < 0.6 else 0
        rework_hours = round(bug_count * random.uniform(0.5, 3), 1) if bug_count > 0 else 0.0

        # Inject some missing values for realism
        if random.random() < 0.02:
            hours_worked_val = None
        else:
            hours_worked_val = hours_worked

        task_rows.append({
            "Task_ID": task_id,
            "Project_ID": proj["Project_ID"],
            "Employee_ID": employee_id,
            "Employee_Name": employee_names[employee_id],
            "Task_Name": f"{random.choice(task_types)} task #{task_counter}",
            "Assigned_Date": assigned_date.strftime("%Y-%m-%d"),
            "Due_Date": due_date.strftime("%Y-%m-%d"),
            "Completed_Date": completed_date.strftime("%Y-%m-%d") if completed_date else None,
            "Hours_Worked": hours_worked_val,
            "Estimated_Hours": est_hours,
            "Task_Status": task_status,
            "Task_Priority": random.choice(task_priorities),
            "Task_Type": random.choice(task_types),
            "Bug_Count": int(bug_count),
            "Rework_Hours": rework_hours
        })

# Duplicate a few task rows on purpose
for _ in range(25):
    task_rows.append(random.choice(task_rows).copy())

task_df = pd.DataFrame(task_rows)
task_df.to_csv("../data/task_data.csv", index=False)
print(f"task_data.csv created -> {task_df.shape[0]} rows, {task_df.shape[1]} columns")

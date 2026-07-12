
-- Tables (loaded from the cleaned CSVs into `projects` and `tasks`):
--   projects(Project_ID, Project_Name, Project_Manager, Team_Name, Department,
--            Project_Type, Start_Date, End_Date, Planned_End_Date, Status,
--            Priority, Budget, Actual_Cost, "Progress_%", Risk_Level, Client,
--            Team_Size, Delay_Days, Cost_Variance, Cost_Variance_%,
--            Is_Delayed, Is_Over_Budget)
--   tasks(Task_ID, Project_ID, Employee_ID, Employee_Name, Task_Name,
--         Assigned_Date, Due_Date, Completed_Date, Hours_Worked,
--         Estimated_Hours, Task_Status, Task_Priority, Task_Type,
--         Bug_Count, Rework_Hours, Is_Completed, Is_Late, Hours_Variance,
--         Efficiency_Ratio)
--



 1.PROJECTS ARE DELAYED AND WHY (linking delay to risk/priority)?

SELECT Project_ID, Project_Name, Department, Project_Manager,
       Priority, Risk_Level, Delay_Days, Budget, Actual_Cost,
       ROUND(Actual_Cost - Budget, 2) AS Cost_Overrun
FROM projects
WHERE Status = 'Delayed'
ORDER BY Delay_Days DESC
LIMIT 20;


 2.MANAGER DELIVERS PROJECTS ON TIME MOST OFTEN? (Success Rate %)

SELECT Project_Manager,
       COUNT(*) AS Total_Projects,
       SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) AS Completed_Projects,
       ROUND(100.0 * SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Success_Rate_Pct
FROM projects
GROUP BY Project_Manager
ORDER BY Success_Rate_Pct DESC;


3. WHICH DEPARTMENTS EXCEED BUDGET, AND BY HOW MUCH?

SELECT Department,
       COUNT(*) AS Total_Projects,
       SUM(Budget) AS Total_Budget,
       SUM(Actual_Cost) AS Total_Actual_Cost,
       ROUND(100.0 * SUM(Actual_Cost) / SUM(Budget), 1) AS Budget_Utilization_Pct,
       ROUND(SUM(Actual_Cost) - SUM(Budget), 2) AS Total_Overrun
FROM projects
GROUP BY Department
HAVING SUM(Actual_Cost) > SUM(Budget)
ORDER BY Total_Overrun DESC;


 4. WHICH PROJECTS HAVE THE HIGHEST RISK?

SELECT Project_ID, Project_Name, Department, Priority, Status,
       Delay_Days, "Cost_Variance_%"
FROM projects
WHERE Risk_Level = 'High'
ORDER BY Delay_Days DESC, "Cost_Variance_%" DESC
LIMIT 20;


5. WHICH TEAMS COMPLETE TASKS FASTEST? (Avg days early/late vs due date)

SELECT p.Team_Name,
       COUNT(t.Task_ID) AS Total_Tasks,
       ROUND(AVG(JULIANDAY(t.Completed_Date) - JULIANDAY(t.Due_Date)), 2) AS Avg_Days_Vs_Due,
       ROUND(100.0 * SUM(CASE WHEN t.Is_Late = 0 THEN 1 ELSE 0 END) / COUNT(t.Task_ID), 1) AS On_Time_Rate_Pct
FROM tasks t
JOIN projects p ON t.Project_ID = p.Project_ID
WHERE t.Task_Status = 'Completed'
GROUP BY p.Team_Name
ORDER BY On_Time_Rate_Pct DESC;


6. WHICH EMPLOYEES ARE MOST PRODUCTIVE? (tasks completed + hours efficiency)

SELECT Employee_Name,
       COUNT(*) AS Tasks_Completed,
       ROUND(SUM(Hours_Worked), 1) AS Total_Hours,
       ROUND(AVG(Estimated_Hours / NULLIF(Hours_Worked, 0)), 2) AS Avg_Efficiency_Ratio,
       SUM(Bug_Count) AS Total_Bugs
FROM tasks
WHERE Task_Status = 'Completed'
GROUP BY Employee_Name
ORDER BY Tasks_Completed DESC
LIMIT 15;


 7. WHAT CAUSES PROJECT DELAYS? (correlate delay with risk, priority, team size)

SELECT Risk_Level, Priority,
       COUNT(*) AS Num_Projects,
       ROUND(AVG(Delay_Days), 1) AS Avg_Delay_Days,
       ROUND(AVG(Team_Size), 1) AS Avg_Team_Size
FROM projects
WHERE Status = 'Delayed'
GROUP BY Risk_Level, Priority
ORDER BY Avg_Delay_Days DESC;


8. HOW CAN COSTS BE REDUCED? (highest cost overrun projects + common traits)

SELECT Department, Project_Type,
       COUNT(*) AS Num_Projects,
       ROUND(AVG("Cost_Variance_%"), 1) AS Avg_Cost_Variance_Pct,
       ROUND(SUM(Actual_Cost - Budget), 2) AS Total_Overrun
FROM projects
WHERE Actual_Cost > Budget
GROUP BY Department, Project_Type
ORDER BY Total_Overrun DESC
LIMIT 10;


9. WHICH PROJECTS REQUIRE IMMEDIATE ATTENTION?
(High risk + Delayed + Over budget = triple red flag)

SELECT Project_ID, Project_Name, Department, Project_Manager,
       Status, Risk_Level, Delay_Days,
       ROUND("Cost_Variance_%", 1) AS Cost_Variance_Pct
FROM projects
WHERE Risk_Level = 'High'
  AND Status = 'Delayed'
  AND Actual_Cost > Budget
ORDER BY Delay_Days DESC, "Cost_Variance_%" DESC;


-10. EXECUTIVE SUMMARY KPI QUERY (single-row snapshot for the exec dashboard)

SELECT
  COUNT(*) AS Total_Projects,
  SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) AS Completed_Projects,
  SUM(CASE WHEN Status = 'Delayed' THEN 1 ELSE 0 END) AS Delayed_Projects,
  ROUND(AVG("Progress_%"), 1) AS Avg_Completion_Pct,
  ROUND(100.0 * SUM(Actual_Cost) / SUM(Budget), 1) AS Budget_Utilization_Pct,
  ROUND(100.0 * SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) /
        SUM(CASE WHEN Status IN ('Completed','Delayed') THEN 1 ELSE 0 END), 1) AS Success_Rate_Pct
FROM projects;

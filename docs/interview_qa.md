# Interview Questions & Answers

## Project Overview

**Q: Walk me through this project.**
A: A mock software company runs 300+ projects and had no single view of health across delivery, cost, and risk. I built an end-to-end pipeline — cleaned and merged project + task data, ran SQL/Python analysis to answer specific business questions, and delivered both an Excel and a Power BI dashboard so leadership could self-serve the answers instead of asking an analyst every time. I also managed the project itself using PM practices — charter, timeline, risk log, status updates — so the project demonstrates both skill sets, not just one described alongside the other.

**Q: Why did you pick this project for a Google Apprenticeship application?**
A: The apprenticeship blends technical and program/project skills. I wanted one project where those aren't two separate exercises — the dashboard *is* the analysis, and the way I planned and delivered it *is* the project management. It's also close to real day-to-day work: most business problems need both "what does the data say" and "how do we act on it in an organized way."

## Data & Technical

**Q: How did you handle missing data, and why those specific choices?**
A: I didn't default to dropping rows. For `Risk_Level`, a missing value is meaningful — it means the project wasn't risk-assessed, so I labeled it "Not Assessed" instead of hiding it. For `Team_Size`, I used the department median rather than the global mean, since team size structurally differs by department (e.g., Engineering vs. QA). For `Hours_Worked`, a blank meant no time had been logged yet, so I filled it with 0 rather than an average, which would have overstated effort.

**Q: Why SQL *and* Python *and* Excel *and* Power BI — isn't that redundant?**
A: They serve different audiences. SQL is how I'd pull answers directly from a database on demand. Python/Pandas is where the heavier cleaning, merging, and exploratory work happens. Excel is what most managers already know how to use day-to-day — the dashboard uses live formulas, not hardcoded numbers, so it updates if new data is dropped in. Power BI is for a more polished, interactive, multi-page executive view with drill-through. In a real company you'd rarely need only one of these.

**Q: What's the difference between `Cost_Variance` and `Cost_Variance_%`, and why report both?**
A: `Cost_Variance` is the absolute rupee overrun (Actual − Budget) — useful for knowing total financial exposure. `Cost_Variance_%` normalizes that against the project's budget size, so a ₹50K overrun on a ₹100K project (50% over) is flagged as more concerning than the same ₹50K overrun on a ₹5M project (1% over). Reporting only one hides that distinction.

**Q: How did you validate your SQL queries were correct?**
A: I loaded the cleaned CSVs into a real SQLite database and executed every query programmatically, checking each returned valid results with no syntax or logic errors, rather than just writing SQL that looked plausible.

**Q: Your dataset is synthetic — how do you defend that in an interview?**
A: I say it directly and don't overclaim. I generated the data with realistic distributions (e.g., ~36% delay rate, missing values, duplicates, correlated risk/priority/delay patterns) specifically so the analysis has real texture to work with — the skills (cleaning, SQL, dashboarding, communicating insight) transfer directly to real company data. It's a transparent portfolio project, not a claim of having secured real company data.

## Analysis & Insights

**Q: What was your most interesting/surprising finding?**
A: That 51% of projects were over budget, but only 36% were formally "Delayed" — meaning a lot of projects run over cost even when they finish on schedule. That's a signal that cost tracking and timeline tracking are being managed somewhat separately, which is itself a finding worth reporting.

**Q: If you had one more week, what would you add?**
A: An automated alert layer — flag a project the moment it crosses, say, 85% budget utilization while under 70% progress, rather than waiting until it's already over. I'd also add a time-series/cohort view to see if delay rates are improving or worsening quarter over quarter.

## Project Management

**Q: How did you scope and manage this project?**
A: I wrote a one-page charter defining the business question and success criteria first, broke the work into phases (data → cleaning → analysis → dashboard → documentation), and tracked it against a simple timeline. I kept a short risk log (e.g., "risk: dataset too clean to be realistic — mitigation: intentionally inject missing values/duplicates") and did a retrospective at the end on what I'd do differently.

**Q: What would you have done differently in how you managed this project?**
A: I'd build the KPI list and Power BI wireframe *before* finalizing the dataset schema — I added a couple of derived columns (like `Cost_Variance_%`) after I'd already started building charts, which meant re-running earlier steps. Locking the "definition of done" for the data model earlier would have saved rework — a lesson I'd apply directly to real project scoping.

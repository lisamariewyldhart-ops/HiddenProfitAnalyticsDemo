import pandas as pd
import pulp


def run_assignment_optimizer(csv_file="assignment_data.csv"):
    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    data = pd.read_csv(csv_file)

    # -----------------------------
    # VALIDATE INPUT DATA
    # -----------------------------
    required_columns = {
        "Employee",
        "Task",
        "Cost",
        "CurrentAssignment"
    }

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    if data[list(required_columns)].isnull().any().any():
        raise ValueError(
            "The CSV contains blank values in one or more required columns."
        )

    data["Cost"] = pd.to_numeric(
        data["Cost"],
        errors="coerce"
    )

    data["CurrentAssignment"] = pd.to_numeric(
        data["CurrentAssignment"],
        errors="coerce"
    )

    if data["Cost"].isnull().any():
        raise ValueError(
            "All Cost values must be numeric."
        )

    if data["CurrentAssignment"].isnull().any():
        raise ValueError(
            "CurrentAssignment values must be 0 or 1."
        )

    if not data["CurrentAssignment"].isin([0, 1]).all():
        raise ValueError(
            "CurrentAssignment values must be either 0 or 1."
        )

    duplicates = data.duplicated(
        subset=["Employee", "Task"]
    )

    if duplicates.any():
        raise ValueError(
            "Duplicate Employee/Task combinations were found."
        )

    # -----------------------------
    # BUILD SETS
    # -----------------------------
    employees = data["Employee"].unique().tolist()
    tasks = data["Task"].unique().tolist()

    # -----------------------------
    # CHECK ALL EMPLOYEE-TASK COMBINATIONS
    # -----------------------------
    expected_combinations = {
        (employee, task)
        for employee in employees
        for task in tasks
    }

    actual_combinations = set(
        zip(data["Employee"], data["Task"])
    )

    missing_combinations = (
        expected_combinations - actual_combinations
    )

    if missing_combinations:
        missing_text = ", ".join(
            f"{employee} / {task}"
            for employee, task in sorted(missing_combinations)
        )

        raise ValueError(
            f"Missing assignment cost data for: {missing_text}"
        )

    # -----------------------------
    # VALIDATE CURRENT ASSIGNMENTS
    # -----------------------------
    current_task_counts = (
        data.groupby("Task")["CurrentAssignment"].sum()
    )

    if not (current_task_counts == 1).all():
        raise ValueError(
            "Each task must have exactly one current assignment."
        )

    current_employee_counts = (
        data.groupby("Employee")["CurrentAssignment"].sum()
    )

    if (current_employee_counts > 1).any():
        raise ValueError(
            "An employee cannot currently be assigned to more than one task."
        )

    # -----------------------------
    # CREATE COST DICTIONARY
    # -----------------------------
    assignment_cost = {
        (row["Employee"], row["Task"]): row["Cost"]
        for _, row in data.iterrows()
    }

    # -----------------------------
    # CREATE OPTIMIZATION MODEL
    # -----------------------------
    model = pulp.LpProblem(
        "Assignment_Optimizer",
        pulp.LpMinimize
    )

    # -----------------------------
    # DECISION VARIABLES
    # -----------------------------
    x = pulp.LpVariable.dicts(
        "Assign",
        (employees, tasks),
        cat="Binary"
    )

    # -----------------------------
    # OBJECTIVE FUNCTION
    # -----------------------------
    model += pulp.lpSum(
        assignment_cost[(employee, task)]
        * x[employee][task]
        for employee in employees
        for task in tasks
    )

    # -----------------------------
    # CONSTRAINTS
    # -----------------------------
    for task in tasks:
        model += pulp.lpSum(
            x[employee][task]
            for employee in employees
        ) == 1

    for employee in employees:
        model += pulp.lpSum(
            x[employee][task]
            for task in tasks
        ) <= 1

    # -----------------------------
    # SOLVE MODEL
    # -----------------------------
    model.solve(
        pulp.PULP_CBC_CMD(msg=False)
    )

    status = pulp.LpStatus[model.status]

    if status != "Optimal":
        raise ValueError(
            f"No optimal assignment could be found. Status: {status}"
        )

    # -----------------------------
    # BUILD OPTIMIZED RESULTS
    # -----------------------------
    assignments = []

    for employee in employees:
        for task in tasks:
            if pulp.value(x[employee][task]) == 1:
                assignments.append(
                    {
                        "Employee": employee,
                        "Task": task,
                        "Cost": assignment_cost[
                            (employee, task)
                        ]
                    }
                )

    results_df = pd.DataFrame(assignments)

    optimized_cost = pulp.value(model.objective)

    # -----------------------------
    # CALCULATE CURRENT COST
    # -----------------------------
    current_cost = (
        data["Cost"] * data["CurrentAssignment"]
    ).sum()

    savings = current_cost - optimized_cost

    savings_percent = (
        (savings / current_cost) * 100
        if current_cost > 0
        else 0
    )

    # -----------------------------
    # BUILD CURRENT ASSIGNMENT TABLE
    # -----------------------------
    current_assignments = data[
        data["CurrentAssignment"] == 1
    ][["Employee", "Task", "Cost"]].copy()

    current_assignments = current_assignments.rename(
        columns={
            "Task": "CurrentTask",
            "Cost": "CurrentCost"
        }
    )

    optimized_assignments = results_df.rename(
        columns={
            "Task": "OptimizedTask",
            "Cost": "OptimizedCost"
        }
    )

    comparison_df = pd.merge(
        current_assignments,
        optimized_assignments,
        on="Employee",
        how="outer"
    )

    comparison_df["Changed"] = (
        comparison_df["CurrentTask"]
        != comparison_df["OptimizedTask"]
    )

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------
    return {
        "status": status,
        "assignments": results_df,
        "comparison": comparison_df,
        "current_cost": current_cost,
        "optimized_cost": optimized_cost,
        "savings": savings,
        "savings_percent": savings_percent
    }

# -----------------------------
# RUN DIRECTLY FOR TESTING
# -----------------------------
if __name__ == "__main__":
    results = run_assignment_optimizer()

    print("\nAssignment Optimizer")
    print("--------------------")

    print(f"Status: {results['status']}")

    print("\nRecommended Assignments:")

    for _, row in results["assignments"].iterrows():
        print(
            f"{row['Employee']} -> "
            f"{row['Task']} | "
            f"Cost: ${row['Cost']:,.2f}"
        )

    print("\nAssignment Changes:")

    for _, row in results["comparison"].iterrows():
        if row["Changed"]:
            print(
                f"{row['Employee']}: "
                f"{row['CurrentTask']} -> "
                f"{row['OptimizedTask']}"
            )
        else:
            print(
                f"{row['Employee']}: "
                f"No change"
            )
             
    print(
        f"\nCurrent Total Cost: "
        f"${results['current_cost']:,.2f}"
    )

    print(
        f"Optimized Total Cost: "
        f"${results['optimized_cost']:,.2f}"
    )

    print(
        f"Potential Savings: "
        f"${results['savings']:,.2f}"
    )

    print(
        f"Savings Percentage: "
        f"{results['savings_percent']:.2f}%"
    )
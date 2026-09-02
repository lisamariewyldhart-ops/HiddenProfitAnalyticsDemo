import pandas as pd
import pulp


def run_assignment_optimizer(csv_file="assignment_data.csv"):
    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    try:
        data = pd.read_csv(csv_file)

    except pd.errors.EmptyDataError:
        raise ValueError(
            "The Assignment CSV is empty. "
            "Please download the Assignment template, enter your data, "
            "and upload the completed file."
        )

    except pd.errors.ParserError:
        raise ValueError(
            "The Assignment CSV could not be read correctly. "
            "Please make sure it is a valid CSV file and has not been "
            "merged, reformatted, or saved with an unusual delimiter."
        )

    if data.empty:
        raise ValueError(
            "The Assignment CSV does not contain any assignment data."
        )

    # Remove accidental spaces from column names
    data.columns = data.columns.str.strip()

    # -----------------------------
    # VALIDATE REQUIRED COLUMNS
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
            "Your Assignment file is missing the required column(s): "
            + ", ".join(sorted(missing_columns))
            + ". Please use the downloadable Assignment CSV template "
            "and keep the column names exactly as shown."
        )

    # -----------------------------
    # CLEAN TEXT FIELDS
    # -----------------------------
    data["Employee"] = (
        data["Employee"]
        .astype(str)
        .str.strip()
    )

    data["Task"] = (
        data["Task"]
        .astype(str)
        .str.strip()
    )

    if (
        data["Employee"].eq("").any()
        or data["Task"].eq("").any()
    ):
        raise ValueError(
            "Employee and Task names cannot be blank."
        )

    # -----------------------------
    # CHECK FOR BLANK REQUIRED VALUES
    # -----------------------------
    if data[
        ["Employee", "Task", "Cost", "CurrentAssignment"]
    ].isnull().any().any():
        raise ValueError(
            "The Assignment file contains blank values. "
            "Every row must include an Employee, Task, Cost, "
            "and CurrentAssignment value."
        )

    # -----------------------------
    # VALIDATE COST
    # -----------------------------
    data["Cost"] = pd.to_numeric(
        data["Cost"],
        errors="coerce"
    )

    if data["Cost"].isnull().any():
        raise ValueError(
            "One or more Cost values are not numeric. "
            "Enter numbers only in the Cost column."
        )

    if (data["Cost"] < 0).any():
        raise ValueError(
            "Cost values cannot be negative."
        )

    # -----------------------------
    # VALIDATE CURRENT ASSIGNMENT
    # -----------------------------
    data["CurrentAssignment"] = pd.to_numeric(
        data["CurrentAssignment"],
        errors="coerce"
    )

    if data["CurrentAssignment"].isnull().any():
        raise ValueError(
            "CurrentAssignment must contain only 0 or 1. "
            "Use 1 for the employee's current task and 0 otherwise."
        )

    if not data["CurrentAssignment"].isin([0, 1]).all():
        raise ValueError(
            "CurrentAssignment must contain only 0 or 1. "
            "Use 1 for a current assignment and 0 for all other combinations."
        )

    # -----------------------------
    # CHECK FOR DUPLICATE EMPLOYEE-TASK COMBINATIONS
    # -----------------------------
    duplicate_rows = data.duplicated(
        subset=["Employee", "Task"],
        keep=False
    )

    if duplicate_rows.any():
        duplicate_pairs = (
            data.loc[
                duplicate_rows,
                ["Employee", "Task"]
            ]
            .drop_duplicates()
            .apply(
                lambda row: f"{row['Employee']} - {row['Task']}",
                axis=1
            )
            .tolist()
        )

        raise ValueError(
            "Each Employee-Task combination must appear only once. "
            "Please remove duplicate combinations: "
            + ", ".join(duplicate_pairs)
            + "."
        )   

    # -----------------------------
    # BUILD SETS
    # -----------------------------
    employees = data["Employee"].unique().tolist()
    tasks = data["Task"].unique().tolist()

    if not employees:
        raise ValueError(
            "No employees were found in the Assignment file."
        )

    if not tasks:
        raise ValueError(
            "No tasks were found in the Assignment file."
        )

    if len(tasks) > len(employees):
        raise ValueError(
            f"The file contains {len(tasks)} tasks but only "
            f"{len(employees)} employees. "
            "This version requires at least as many employees as tasks "
            "because each employee may receive at most one task."
        )

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
            "Assignment cost information is missing for: "
            f"{missing_text}. "
            "Every employee must have a Cost row for every task."
        )

    # -----------------------------
    # VALIDATE CURRENT ASSIGNMENTS
    # -----------------------------
    current_task_counts = (
        data.groupby("Task")["CurrentAssignment"].sum()
    )

    invalid_tasks = current_task_counts[
        current_task_counts != 1
    ]

    if not invalid_tasks.empty:
        task_text = ", ".join(
            invalid_tasks.index.tolist()
        )

        raise ValueError(
            "Each task must have exactly one current assignment. "
            f"Please check: {task_text}."
        )

    current_employee_counts = (
        data.groupby("Employee")["CurrentAssignment"].sum()
    )

    invalid_employees = current_employee_counts[
        current_employee_counts > 1
    ]

    if not invalid_employees.empty:
        employee_text = ", ".join(
            invalid_employees.index.tolist()
        )

        raise ValueError(
            "An employee cannot currently be assigned to more than "
            f"one task in this version. Please check: {employee_text}."
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
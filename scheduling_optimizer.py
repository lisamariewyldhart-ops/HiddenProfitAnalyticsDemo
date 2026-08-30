import pandas as pd
import pulp


def run_scheduling_optimizer(
    cost_file="scheduling_costs.csv",
    requirements_file="scheduling_requirements.csv",
    availability_file="scheduling_availability.csv",
    current_file="scheduling_current.csv"
):
    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    cost_data = pd.read_csv(cost_file)
    requirements_data = pd.read_csv(requirements_file)
    availability_data = pd.read_csv(availability_file)
    current_data = pd.read_csv(current_file)

    # -----------------------------
    # IDENTIFY SETS
    # -----------------------------
    employees = cost_data["Employee"].tolist()

    shifts = [
        column
        for column in cost_data.columns
        if column != "Employee"
    ]

    # -----------------------------
    # CREATE DICTIONARIES
    # -----------------------------
    labor_cost = {
        (row["Employee"], shift): row[shift]
        for _, row in cost_data.iterrows()
        for shift in shifts
    }

    required_employees = {
        row["Shift"]: row["RequiredEmployees"]
        for _, row in requirements_data.iterrows()
    }

    availability = {
        (row["Employee"], shift): row[shift]
        for _, row in availability_data.iterrows()
        for shift in shifts
    }

    current_shift = {
        row["Employee"]: row["Shift"]
        for _, row in current_data.iterrows()
    }

    # -----------------------------
    # VALIDATE CURRENT SCHEDULE
    # -----------------------------
    for employee in employees:
        if employee not in current_shift:
            raise ValueError(
                f"Missing current schedule for {employee}."
            )

        shift = current_shift[employee]

        if shift not in shifts:
            raise ValueError(
                f"{employee} has an unknown current shift: {shift}"
            )

        if availability[(employee, shift)] != 1:
            raise ValueError(
                f"{employee} is currently assigned to {shift}, "
                "but is marked unavailable."
            )

    # -----------------------------
    # CREATE OPTIMIZATION MODEL
    # -----------------------------
    model = pulp.LpProblem(
        "Scheduling_Optimizer",
        pulp.LpMinimize
    )

    # -----------------------------
    # DECISION VARIABLES
    # -----------------------------
    assign = pulp.LpVariable.dicts(
        "Assign",
        (employees, shifts),
        cat="Binary"
    )

    # -----------------------------
    # OBJECTIVE FUNCTION
    # -----------------------------
    model += pulp.lpSum(
        labor_cost[(employee, shift)]
        * assign[employee][shift]
        for employee in employees
        for shift in shifts
    )

    # -----------------------------
    # STAFFING REQUIREMENTS
    # -----------------------------
    for shift in shifts:
        model += pulp.lpSum(
            assign[employee][shift]
            for employee in employees
        ) >= required_employees[shift]

    # -----------------------------
    # AVAILABILITY CONSTRAINTS
    # -----------------------------
    for employee in employees:
        for shift in shifts:
            model += (
                assign[employee][shift]
                <= availability[(employee, shift)]
            )

    # -----------------------------
    # MAXIMUM ONE SHIFT PER EMPLOYEE
    # -----------------------------
    for employee in employees:
        model += pulp.lpSum(
            assign[employee][shift]
            for shift in shifts
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
            f"No optimal schedule could be found. Status: {status}"
        )

    # -----------------------------
    # CURRENT COST
    # -----------------------------
    current_total_cost = sum(
        labor_cost[
            (employee, current_shift[employee])
        ]
        for employee in employees
    )

    # -----------------------------
    # BUILD SCHEDULE COMPARISON
    # -----------------------------
    schedule_rows = []

    for employee in employees:
        optimized_shift = None

        for shift in shifts:
            if pulp.value(assign[employee][shift]) == 1:
                optimized_shift = shift
                break

        changed = (
            current_shift[employee]
            != optimized_shift
        )

        current_cost = labor_cost[
            (employee, current_shift[employee])
        ]

        optimized_cost = (
            labor_cost[(employee, optimized_shift)]
            if optimized_shift is not None
            else 0
        )

        schedule_rows.append(
            {
                "Employee": employee,
                "CurrentShift": current_shift[employee],
                "CurrentCost": current_cost,
                "OptimizedShift": optimized_shift,
                "OptimizedCost": optimized_cost,
                "Changed": changed
            }
        )

    schedule_comparison = pd.DataFrame(
        schedule_rows
    )

    # -----------------------------
    # BUSINESS IMPACT
    # -----------------------------
    optimized_total_cost = pulp.value(
        model.objective
    )

    savings = (
        current_total_cost
        - optimized_total_cost
    )

    savings_percent = (
        (savings / current_total_cost) * 100
        if current_total_cost > 0
        else 0
    )

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------
    return {
        "status": status,
        "schedule_comparison": schedule_comparison,
        "current_total_cost": current_total_cost,
        "optimized_total_cost": optimized_total_cost,
        "savings": savings,
        "savings_percent": savings_percent
    }


# -----------------------------
# RUN DIRECTLY FOR TESTING
# -----------------------------
if __name__ == "__main__":
    results = run_scheduling_optimizer()

    print("\nScheduling Optimizer")
    print("--------------------")

    print(f"Status: {results['status']}")

    print("\nSchedule Changes:")

    for _, row in results[
        "schedule_comparison"
    ].iterrows():

        if row["Changed"]:
            print(
                f"{row['Employee']}: "
                f"{row['CurrentShift']} -> "
                f"{row['OptimizedShift']}"
            )
        else:
            print(
                f"{row['Employee']}: No change"
            )

    print(
        f"\nCurrent Labor Cost: "
        f"${results['current_total_cost']:,.2f}"
    )

    print(
        f"Optimized Labor Cost: "
        f"${results['optimized_total_cost']:,.2f}"
    )

    print(
        f"Potential Savings: "
        f"${results['savings']:,.2f}"
    )

    print(
        f"Savings Percentage: "
        f"{results['savings_percent']:.2f}%"
    )
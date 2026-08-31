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
    try:
        cost_data = pd.read_csv(cost_file)
        requirements_data = pd.read_csv(requirements_file)
        availability_data = pd.read_csv(availability_file)
        current_data = pd.read_csv(current_file)

    except pd.errors.EmptyDataError:
        raise ValueError(
            "One of the Scheduling CSV files is empty. "
            "Please download the Scheduling templates, enter your data, "
            "and upload all four completed files."
        )

    except pd.errors.ParserError:
        raise ValueError(
            "One of the Scheduling CSV files could not be read correctly. "
            "Please make sure all four files are valid CSV files."
        )

    if cost_data.empty:
        raise ValueError(
            "The Scheduling Cost file does not contain any employee data."
        )

    if requirements_data.empty:
        raise ValueError(
            "The Staffing Requirements file does not contain any shift data."
        )

    if availability_data.empty:
        raise ValueError(
            "The Availability file does not contain any employee data."
        )

    if current_data.empty:
        raise ValueError(
            "The Current Schedule file does not contain any assignments."
        )

    cost_data.columns = cost_data.columns.str.strip()
    requirements_data.columns = requirements_data.columns.str.strip()
    availability_data.columns = availability_data.columns.str.strip()
    current_data.columns = current_data.columns.str.strip()

    # -----------------------------
    # VALIDATE REQUIRED COLUMNS
    # -----------------------------
    cost_required = {"Employee"}
    requirements_required = {
        "Shift",
        "RequiredEmployees"
    }
    availability_required = {"Employee"}
    current_required = {
        "Employee",
        "Shift"
    }

    missing_cost_columns = (
        cost_required - set(cost_data.columns)
    )

    missing_requirements_columns = (
        requirements_required - set(requirements_data.columns)
    )

    missing_availability_columns = (
        availability_required - set(availability_data.columns)
    )

    missing_current_columns = (
        current_required - set(current_data.columns)
    )

    if missing_cost_columns:
        raise ValueError(
            "Your Scheduling Cost file is missing the required column(s): "
            + ", ".join(sorted(missing_cost_columns))
            + ". Please use the downloadable Scheduling Cost template."
        )

    if missing_requirements_columns:
        raise ValueError(
            "Your Staffing Requirements file is missing the required column(s): "
            + ", ".join(sorted(missing_requirements_columns))
            + ". Please use the downloadable Staffing Requirements template."
        )

    if missing_availability_columns:
        raise ValueError(
            "Your Availability file is missing the required column(s): "
            + ", ".join(sorted(missing_availability_columns))
            + ". Please use the downloadable Availability template."
        )

    if missing_current_columns:
        raise ValueError(
            "Your Current Schedule file is missing the required column(s): "
            + ", ".join(sorted(missing_current_columns))
            + ". Please use the downloadable Current Schedule template."
        )

    # -----------------------------
    # CLEAN TEXT FIELDS
    # -----------------------------
    cost_data["Employee"] = (
        cost_data["Employee"]
        .astype(str)
        .str.strip()
    )

    availability_data["Employee"] = (
        availability_data["Employee"]
        .astype(str)
        .str.strip()
    )

    requirements_data["Shift"] = (
        requirements_data["Shift"]
        .astype(str)
        .str.strip()
    )

    current_data["Employee"] = (
        current_data["Employee"]
        .astype(str)
        .str.strip()
    )

    current_data["Shift"] = (
        current_data["Shift"]
        .astype(str)
        .str.strip()
    )

    # -----------------------------
    # IDENTIFY SETS
    # -----------------------------
    employees = cost_data["Employee"].tolist()

    shifts = [
        column
        for column in cost_data.columns
        if column != "Employee"
    ]

    if not shifts:
        raise ValueError(
            "No shift cost columns were found in the Scheduling Cost file."
        )

    # -----------------------------
    # CHECK DUPLICATES
    # -----------------------------
    if cost_data["Employee"].duplicated().any():
        raise ValueError(
            "Duplicate employee names were found in the Scheduling Cost file."
        )

    if availability_data["Employee"].duplicated().any():
        raise ValueError(
            "Duplicate employee names were found in the Availability file."
        )

    if requirements_data["Shift"].duplicated().any():
        raise ValueError(
            "Duplicate shift names were found in the Staffing Requirements file."
        )

    if current_data["Employee"].duplicated().any():
        raise ValueError(
            "Duplicate employee names were found in the Current Schedule file."
        )

    # -----------------------------
    # VALIDATE SHIFT MATCHING
    # -----------------------------
    requirement_shifts = set(
        requirements_data["Shift"]
    )

    cost_shifts = set(shifts)

    missing_requirement_shifts = (
        cost_shifts - requirement_shifts
    )

    extra_requirement_shifts = (
        requirement_shifts - cost_shifts
    )

    if missing_requirement_shifts:
        raise ValueError(
            "The Staffing Requirements file is missing shift data for: "
            + ", ".join(sorted(missing_requirement_shifts))
        )

    if extra_requirement_shifts:
        raise ValueError(
            "The Staffing Requirements file contains unknown shifts: "
            + ", ".join(sorted(extra_requirement_shifts))
        )

    availability_shifts = {
        column
        for column in availability_data.columns
        if column != "Employee"
    }

    if availability_shifts != cost_shifts:
        missing = cost_shifts - availability_shifts
        extra = availability_shifts - cost_shifts

        message_parts = []

        if missing:
            message_parts.append(
                "missing: " + ", ".join(sorted(missing))
            )

        if extra:
            message_parts.append(
                "unexpected: " + ", ".join(sorted(extra))
            )

        raise ValueError(
            "Availability shift columns do not match the Scheduling Cost file ("
            + "; ".join(message_parts)
            + ")."
        )

    # -----------------------------
    # VALIDATE EMPLOYEE MATCHING
    # -----------------------------
    cost_employees = set(employees)
    availability_employees = set(
        availability_data["Employee"]
    )
    current_employees = set(
        current_data["Employee"]
    )

    if availability_employees != cost_employees:
        raise ValueError(
            "Employee names in the Availability file must match "
            "the Scheduling Cost file exactly."
        )

    if current_employees != cost_employees:
        raise ValueError(
            "Employee names in the Current Schedule file must match "
            "the Scheduling Cost file exactly."
        )

    # -----------------------------
    # VALIDATE NUMERIC DATA
    # -----------------------------
    for shift in shifts:
        cost_data[shift] = pd.to_numeric(
            cost_data[shift],
            errors="coerce"
        )

        if cost_data[shift].isnull().any():
            raise ValueError(
                f"Labor costs for '{shift}' must be numeric."
            )

        if (cost_data[shift] < 0).any():
            raise ValueError(
                f"Labor costs for '{shift}' cannot be negative."
            )

        availability_data[shift] = pd.to_numeric(
            availability_data[shift],
            errors="coerce"
        )

        if availability_data[shift].isnull().any():
            raise ValueError(
                f"Availability values for '{shift}' must be numeric."
            )

        if not availability_data[shift].isin([0, 1]).all():
            raise ValueError(
                f"Availability values for '{shift}' must be 0 or 1."
            )

    requirements_data["RequiredEmployees"] = pd.to_numeric(
        requirements_data["RequiredEmployees"],
        errors="coerce"
    )

    if requirements_data["RequiredEmployees"].isnull().any():
        raise ValueError(
            "RequiredEmployees values must be numeric."
        )

    if (requirements_data["RequiredEmployees"] < 0).any():
        raise ValueError(
            "RequiredEmployees values cannot be negative."
        )

    if not (
        requirements_data["RequiredEmployees"]
        % 1
        == 0
    ).all():
        raise ValueError(
            "RequiredEmployees values must be whole numbers."
        )

    # -----------------------------
    # CREATE DICTIONARIES
    # -----------------------------
    labor_cost = {
        (row["Employee"], shift): row[shift]
        for _, row in cost_data.iterrows()
        for shift in shifts
    }

    required_employees = {
        row["Shift"]: int(row["RequiredEmployees"])
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
    # CHECK STAFFING FEASIBILITY
    # -----------------------------
    total_required = sum(
        required_employees.values()
    )

    if total_required > len(employees):
        raise ValueError(
            f"The schedule requires {total_required} total employee assignments, "
            f"but only {len(employees)} employees are available. "
            "Because this version allows each employee to work at most one shift, "
            "the staffing requirements cannot be met."
        )

    for shift in shifts:
        available_count = sum(
            availability[(employee, shift)]
            for employee in employees
        )

        if available_count < required_employees[shift]:
            raise ValueError(
                f"{shift} requires {required_employees[shift]} employees, "
                f"but only {available_count} employees are available for that shift."
            )

    # -----------------------------
    # VALIDATE CURRENT SCHEDULE
    # -----------------------------
    for employee in employees:
        shift = current_shift[employee]

        if shift not in shifts:
            raise ValueError(
                f"{employee} is currently assigned to an unknown shift: {shift}."
            )

        if availability[(employee, shift)] != 1:
            raise ValueError(
                f"{employee} is currently assigned to {shift}, "
                "but is marked unavailable for that shift."
            )

    current_shift_counts = (
        current_data["Shift"].value_counts()
    )

    for shift in shifts:
        current_count = current_shift_counts.get(
            shift,
            0
        )

        if current_count < required_employees[shift]:
            raise ValueError(
                f"The current schedule assigns {current_count} employees to "
                f"{shift}, but at least {required_employees[shift]} are required."
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
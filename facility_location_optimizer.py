import pandas as pd
import pulp


def run_facility_location_optimizer(
    facility_file="facility_location_data.csv",
    demand_file="facility_demand.csv"
):
    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    facility_data = pd.read_csv(facility_file)
    demand_data = pd.read_csv(demand_file)

    # -----------------------------
    # VALIDATE REQUIRED COLUMNS
    # -----------------------------
    facility_required = {
        "Facility",
        "FixedCost",
        "CurrentOpen"
    }

    demand_required = {
        "Customer",
        "Demand",
        "CurrentFacility"
    }

    missing_facility_columns = (
        facility_required - set(facility_data.columns)
    )

    missing_demand_columns = (
        demand_required - set(demand_data.columns)
    )

    if missing_facility_columns:
        raise ValueError(
            "Missing facility columns: "
            + ", ".join(sorted(missing_facility_columns))
        )

    if missing_demand_columns:
        raise ValueError(
            "Missing demand columns: "
            + ", ".join(sorted(missing_demand_columns))
        )

    # -----------------------------
    # IDENTIFY SETS
    # -----------------------------
    facilities = facility_data["Facility"].tolist()

    customers = [
        column
        for column in facility_data.columns
        if column not in [
            "Facility",
            "FixedCost",
            "CurrentOpen"
        ]
    ]

    # -----------------------------
    # VALIDATE NUMERIC DATA
    # -----------------------------
    facility_data["FixedCost"] = pd.to_numeric(
        facility_data["FixedCost"],
        errors="coerce"
    )

    facility_data["CurrentOpen"] = pd.to_numeric(
        facility_data["CurrentOpen"],
        errors="coerce"
    )

    demand_data["Demand"] = pd.to_numeric(
        demand_data["Demand"],
        errors="coerce"
    )

    if facility_data["FixedCost"].isnull().any():
        raise ValueError(
            "All FixedCost values must be numeric."
        )

    if facility_data["CurrentOpen"].isnull().any():
        raise ValueError(
            "CurrentOpen values must be 0 or 1."
        )

    if not facility_data["CurrentOpen"].isin([0, 1]).all():
        raise ValueError(
            "CurrentOpen values must be either 0 or 1."
        )

    if demand_data["Demand"].isnull().any():
        raise ValueError(
            "All Demand values must be numeric."
        )

    for customer in customers:
        facility_data[customer] = pd.to_numeric(
            facility_data[customer],
            errors="coerce"
        )

        if facility_data[customer].isnull().any():
            raise ValueError(
                f"All service costs for {customer} must be numeric."
            )

    # -----------------------------
    # VALIDATE CUSTOMERS
    # -----------------------------
    demand_customers = set(demand_data["Customer"])

    missing_customers = (
        set(customers) - demand_customers
    )

    if missing_customers:
        raise ValueError(
            "Missing demand data for: "
            + ", ".join(sorted(missing_customers))
        )

    # -----------------------------
    # CREATE DICTIONARIES
    # -----------------------------
    fixed_cost = {
        row["Facility"]: row["FixedCost"]
        for _, row in facility_data.iterrows()
    }

    current_open = {
        row["Facility"]: int(row["CurrentOpen"])
        for _, row in facility_data.iterrows()
    }

    service_cost = {
        (row["Facility"], customer): row[customer]
        for _, row in facility_data.iterrows()
        for customer in customers
    }

    demand = {
        row["Customer"]: row["Demand"]
        for _, row in demand_data.iterrows()
    }

    current_facility = {
        row["Customer"]: row["CurrentFacility"]
        for _, row in demand_data.iterrows()
    }

    # -----------------------------
    # VALIDATE CURRENT CONFIGURATION
    # -----------------------------
    for customer in customers:
        facility = current_facility[customer]

        if facility not in facilities:
            raise ValueError(
                f"{customer} is assigned to unknown facility: {facility}"
            )

        if current_open[facility] != 1:
            raise ValueError(
                f"{customer} is assigned to {facility}, "
                "but that facility is not currently open."
            )

    # -----------------------------
    # CREATE OPTIMIZATION MODEL
    # -----------------------------
    model = pulp.LpProblem(
        "Facility_Location_Optimizer",
        pulp.LpMinimize
    )

    # -----------------------------
    # DECISION VARIABLES
    # -----------------------------
    open_facility = pulp.LpVariable.dicts(
        "Open",
        facilities,
        cat="Binary"
    )

    assign = pulp.LpVariable.dicts(
        "Assign",
        (facilities, customers),
        cat="Binary"
    )

    # -----------------------------
    # OBJECTIVE FUNCTION
    # -----------------------------
    model += (
        pulp.lpSum(
            fixed_cost[facility]
            * open_facility[facility]
            for facility in facilities
        )
        +
        pulp.lpSum(
            service_cost[(facility, customer)]
            * demand[customer]
            * assign[facility][customer]
            for facility in facilities
            for customer in customers
        )
    )

    # -----------------------------
    # CONSTRAINTS
    # -----------------------------
    for customer in customers:
        model += pulp.lpSum(
            assign[facility][customer]
            for facility in facilities
        ) == 1

    for facility in facilities:
        for customer in customers:
            model += (
                assign[facility][customer]
                <= open_facility[facility]
            )

    # -----------------------------
    # SOLVE MODEL
    # -----------------------------
    model.solve(
        pulp.PULP_CBC_CMD(msg=False)
    )

    status = pulp.LpStatus[model.status]

    if status != "Optimal":
        raise ValueError(
            f"No optimal solution could be found. Status: {status}"
        )

    # -----------------------------
    # CURRENT TOTAL COST
    # -----------------------------
    current_fixed_cost = sum(
        fixed_cost[facility]
        * current_open[facility]
        for facility in facilities
    )

    current_service_cost = sum(
        service_cost[
            (current_facility[customer], customer)
        ]
        * demand[customer]
        for customer in customers
    )

    current_total_cost = (
        current_fixed_cost
        + current_service_cost
    )

    # -----------------------------
    # OPTIMIZED TOTAL COST
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
    # FACILITY COMPARISON
    # -----------------------------
    facility_rows = []

    for facility in facilities:
        optimized_open = int(
            pulp.value(
                open_facility[facility]
            ) == 1
        )

        if (
            current_open[facility] == 1
            and optimized_open == 1
        ):
            recommendation = "Keep Open"

        elif (
            current_open[facility] == 1
            and optimized_open == 0
        ):
            recommendation = "Close"

        elif (
            current_open[facility] == 0
            and optimized_open == 1
        ):
            recommendation = "Open"

        else:
            recommendation = "Remain Closed"

        facility_rows.append(
            {
                "Facility": facility,
                "FixedCost": fixed_cost[facility],
                "CurrentOpen": current_open[facility],
                "OptimizedOpen": optimized_open,
                "Recommendation": recommendation
            }
        )

    facility_comparison = pd.DataFrame(
        facility_rows
    )

    # -----------------------------
    # CUSTOMER ASSIGNMENT COMPARISON
    # -----------------------------
    assignment_rows = []

    for customer in customers:
        optimized_facility = None

        for facility in facilities:
            if (
                pulp.value(
                    assign[facility][customer]
                ) == 1
            ):
                optimized_facility = facility
                break

        changed = (
            current_facility[customer]
            != optimized_facility
        )

        assignment_rows.append(
            {
                "Customer": customer,
                "Demand": demand[customer],
                "CurrentFacility":
                    current_facility[customer],
                "OptimizedFacility":
                    optimized_facility,
                "Changed": changed
            }
        )

    assignment_comparison = pd.DataFrame(
        assignment_rows
    )

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------
    return {
        "status": status,
        "current_total_cost":
            current_total_cost,
        "optimized_total_cost":
            optimized_total_cost,
        "savings":
            savings,
        "savings_percent":
            savings_percent,
        "facility_comparison":
            facility_comparison,
        "assignment_comparison":
            assignment_comparison
    }


# -----------------------------
# RUN DIRECTLY FOR TESTING
# -----------------------------
if __name__ == "__main__":
    results = run_facility_location_optimizer()

    print("\nFacility Location Optimizer")
    print("---------------------------")

    print(f"Status: {results['status']}")

    print("\nFacility Recommendations:")

    for _, row in results[
        "facility_comparison"
    ].iterrows():
        print(
            f"{row['Facility']}: "
            f"{row['Recommendation']}"
        )

    print("\nCustomer Assignment Changes:")

    for _, row in results[
        "assignment_comparison"
    ].iterrows():
        if row["Changed"]:
            print(
                f"{row['Customer']}: "
                f"{row['CurrentFacility']} -> "
                f"{row['OptimizedFacility']}"
            )
        else:
            print(
                f"{row['Customer']}: "
                "No change"
            )

    print(
        f"\nCurrent Total Cost: "
        f"${results['current_total_cost']:,.2f}"
    )

    print(
        f"Optimized Total Cost: "
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
import pandas as pd
import pulp


def run_facility_location_optimizer(
    facility_file="facility_location_data.csv",
    demand_file="facility_demand.csv"
):
    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    try:
        facility_data = pd.read_csv(facility_file)
        demand_data = pd.read_csv(demand_file)

    except pd.errors.EmptyDataError:
        raise ValueError(
            "One of the Facility Location CSV files is empty. "
            "Please download the Facility Location templates, enter your data, "
            "and upload both completed files."
        )

    except pd.errors.ParserError:
        raise ValueError(
            "One of the Facility Location CSV files could not be read correctly. "
            "Please make sure both files are valid CSV files."
        )

    if facility_data.empty:
        raise ValueError(
            "The Facility Cost file does not contain any facility data."
        )

    if demand_data.empty:
        raise ValueError(
            "The Customer Demand file does not contain any customer data."
        )

    facility_data.columns = facility_data.columns.str.strip()
    demand_data.columns = demand_data.columns.str.strip()

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
            "Your Facility Cost file is missing the required column(s): "
            + ", ".join(sorted(missing_facility_columns))
            + ". Please use the downloadable Facility Cost template "
              "and keep the column names exactly as shown."
        )

    if missing_demand_columns:
        raise ValueError(
            "Your Customer Demand file is missing the required column(s): "
            + ", ".join(sorted(missing_demand_columns))
            + ". Please use the downloadable Customer Demand template "
              "and keep the column names exactly as shown."
        )

    # -----------------------------
    # CLEAN TEXT FIELDS
    # -----------------------------
    facility_data["Facility"] = (
        facility_data["Facility"]
        .astype(str)
        .str.strip()
    )

    demand_data["Customer"] = (
        demand_data["Customer"]
        .astype(str)
        .str.strip()
    )

    demand_data["CurrentFacility"] = (
        demand_data["CurrentFacility"]
        .astype(str)
        .str.strip()
    )

    if facility_data["Facility"].eq("").any():
        raise ValueError(
            "Facility names cannot be blank."
        )

    if demand_data["Customer"].eq("").any():
        raise ValueError(
            "Customer names cannot be blank."
        )

    if demand_data["CurrentFacility"].eq("").any():
        raise ValueError(
            "CurrentFacility values cannot be blank."
        )

    # -----------------------------
    # CHECK DUPLICATES
    # -----------------------------
    duplicate_facilities = facility_data["Facility"].duplicated(
        keep=False
    )

    if duplicate_facilities.any():
        duplicate_text = ", ".join(
            sorted(
                facility_data.loc[
                    duplicate_facilities,
                    "Facility"
                ].unique()
            )
        )

        raise ValueError(
            "Duplicate facility names were found: "
            f"{duplicate_text}. "
            "Each facility should appear only once."
        )

    duplicate_customers = demand_data["Customer"].duplicated(
        keep=False
    )

    if duplicate_customers.any():
        duplicate_text = ", ".join(
            sorted(
                demand_data.loc[
                    duplicate_customers,
                    "Customer"
                ].unique()
            )
        )

        raise ValueError(
            "Duplicate customer names were found: "
            f"{duplicate_text}. "
            "Each customer should appear only once in the demand file."
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

    if not customers:
        raise ValueError(
            "No customer service-cost columns were found in the Facility Cost file."
        )

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
            "One or more FixedCost values are not numeric."
        )

    if (facility_data["FixedCost"] < 0).any():
        raise ValueError(
            "FixedCost values cannot be negative."
        )

    if facility_data["CurrentOpen"].isnull().any():
        raise ValueError(
            "CurrentOpen must contain only 0 or 1."
        )

    if not facility_data["CurrentOpen"].isin([0, 1]).all():
        raise ValueError(
            "CurrentOpen must contain only 0 or 1. "
            "Use 1 for a currently open facility and 0 otherwise."
        )

    if demand_data["Demand"].isnull().any():
        raise ValueError(
            "One or more Demand values are not numeric."
        )

    if (demand_data["Demand"] < 0).any():
        raise ValueError(
            "Demand values cannot be negative."
        )

    for customer in customers:
        facility_data[customer] = pd.to_numeric(
            facility_data[customer],
            errors="coerce"
        )

        if facility_data[customer].isnull().any():
            raise ValueError(
                f"Service-cost values for '{customer}' must be numeric."
            )

        if (facility_data[customer] < 0).any():
            raise ValueError(
                f"Service-cost values for '{customer}' cannot be negative."
            )

    # -----------------------------
    # VALIDATE CUSTOMER MATCHING
    # -----------------------------
    demand_customers = set(demand_data["Customer"])

    missing_customers = (
        set(customers) - demand_customers
    )

    extra_customers = (
        demand_customers - set(customers)
    )

    if missing_customers:
        raise ValueError(
            "The Customer Demand file is missing data for: "
            + ", ".join(sorted(missing_customers))
            + ". Customer names must match the customer column names "
              "in the Facility Cost file."
        )

    if extra_customers:
        raise ValueError(
            "The Customer Demand file contains customer names that do not "
            "exist as service-cost columns in the Facility Cost file: "
            + ", ".join(sorted(extra_customers))
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
                f"{customer} is currently assigned to '{facility}', "
                "but that facility does not exist in the Facility Cost file."
            )

        if current_open[facility] != 1:
            raise ValueError(
                f"{customer} is currently assigned to {facility}, "
                "but that facility is marked CurrentOpen = 0."
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
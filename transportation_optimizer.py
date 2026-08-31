import pandas as pd
import pulp


def run_transportation_optimizer(
    cost_file="transportation_costs.csv",
    supply_file="transportation_supply.csv",
    demand_file="transportation_demand.csv",
    current_file="transportation_current.csv"
):
    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    try:
        cost_data = pd.read_csv(cost_file)
        supply_data = pd.read_csv(supply_file)
        demand_data = pd.read_csv(demand_file)
        current_data = pd.read_csv(current_file)

    except pd.errors.EmptyDataError:
        raise ValueError(
            "One of the Transportation CSV files is empty. "
            "Please download the Transportation templates, enter your data, "
            "and upload all four completed files."
        )

    except pd.errors.ParserError:
        raise ValueError(
            "One of the Transportation CSV files could not be read correctly. "
            "Please make sure all four files are valid CSV files."
        )

    if cost_data.empty:
        raise ValueError(
            "The Transportation Cost file does not contain any source data."
        )

    if supply_data.empty:
        raise ValueError(
            "The Supply file does not contain any source data."
        )

    if demand_data.empty:
        raise ValueError(
            "The Demand file does not contain any destination data."
        )

    if current_data.empty:
        raise ValueError(
            "The Current Shipping Plan file does not contain any shipment data."
        )

    cost_data.columns = cost_data.columns.str.strip()
    supply_data.columns = supply_data.columns.str.strip()
    demand_data.columns = demand_data.columns.str.strip()
    current_data.columns = current_data.columns.str.strip()

    # -----------------------------
    # VALIDATE REQUIRED COLUMNS
    # -----------------------------
    cost_required = {"Source"}
    supply_required = {"Source", "Supply"}
    demand_required = {"Destination", "Demand"}
    current_required = {
        "Source",
        "Destination",
        "Quantity"
    }

    missing_cost_columns = (
        cost_required - set(cost_data.columns)
    )

    missing_supply_columns = (
        supply_required - set(supply_data.columns)
    )

    missing_demand_columns = (
        demand_required - set(demand_data.columns)
    )

    missing_current_columns = (
        current_required - set(current_data.columns)
    )

    if missing_cost_columns:
        raise ValueError(
            "Your Transportation Cost file is missing the required column(s): "
            + ", ".join(sorted(missing_cost_columns))
            + ". Please use the downloadable Transportation Cost template "
              "and keep the column names exactly as shown."
        )

    if missing_supply_columns:
        raise ValueError(
            "Your Supply file is missing the required column(s): "
            + ", ".join(sorted(missing_supply_columns))
            + ". Please use the downloadable Supply template."
        )

    if missing_demand_columns:
        raise ValueError(
            "Your Demand file is missing the required column(s): "
            + ", ".join(sorted(missing_demand_columns))
            + ". Please use the downloadable Demand template."
        )

    if missing_current_columns:
        raise ValueError(
            "Your Current Shipping Plan file is missing the required column(s): "
            + ", ".join(sorted(missing_current_columns))
            + ". Please use the downloadable Current Shipping template."
        )

    # -----------------------------
    # CLEAN TEXT FIELDS
    # -----------------------------
    cost_data["Source"] = (
        cost_data["Source"]
        .astype(str)
        .str.strip()
    )

    supply_data["Source"] = (
        supply_data["Source"]
        .astype(str)
        .str.strip()
    )

    demand_data["Destination"] = (
        demand_data["Destination"]
        .astype(str)
        .str.strip()
    )

    current_data["Source"] = (
        current_data["Source"]
        .astype(str)
        .str.strip()
    )

    current_data["Destination"] = (
        current_data["Destination"]
        .astype(str)
        .str.strip()
    )

    # -----------------------------
    # IDENTIFY SETS
    # -----------------------------
    sources = cost_data["Source"].tolist()

    destinations = [
        column
        for column in cost_data.columns
        if column != "Source"
    ]

    if not destinations:
        raise ValueError(
            "No destination cost columns were found in the Transportation Cost file."
        )

    # -----------------------------
    # CHECK DUPLICATES
    # -----------------------------
    duplicate_sources = cost_data["Source"].duplicated(
        keep=False
    )

    if duplicate_sources.any():
        duplicate_text = ", ".join(
            sorted(
                cost_data.loc[
                    duplicate_sources,
                    "Source"
                ].unique()
            )
        )

        raise ValueError(
            "Duplicate source names were found in the Transportation Cost file: "
            f"{duplicate_text}."
        )

    if supply_data["Source"].duplicated().any():
        raise ValueError(
            "Duplicate source names were found in the Supply file."
        )

    if demand_data["Destination"].duplicated().any():
        raise ValueError(
            "Duplicate destination names were found in the Demand file."
        )

    # -----------------------------
    # VALIDATE NUMERIC DATA
    # -----------------------------
    supply_data["Supply"] = pd.to_numeric(
        supply_data["Supply"],
        errors="coerce"
    )

    demand_data["Demand"] = pd.to_numeric(
        demand_data["Demand"],
        errors="coerce"
    )

    current_data["Quantity"] = pd.to_numeric(
        current_data["Quantity"],
        errors="coerce"
    )

    if supply_data["Supply"].isnull().any():
        raise ValueError(
            "One or more Supply values are not numeric."
        )

    if (supply_data["Supply"] < 0).any():
        raise ValueError(
            "Supply values cannot be negative."
        )

    if demand_data["Demand"].isnull().any():
        raise ValueError(
            "One or more Demand values are not numeric."
        )

    if (demand_data["Demand"] < 0).any():
        raise ValueError(
            "Demand values cannot be negative."
        )

    if current_data["Quantity"].isnull().any():
        raise ValueError(
            "One or more current shipment quantities are not numeric."
        )

    if (current_data["Quantity"] < 0).any():
        raise ValueError(
            "Current shipment quantities cannot be negative."
        )

    for destination in destinations:
        cost_data[destination] = pd.to_numeric(
            cost_data[destination],
            errors="coerce"
        )

        if cost_data[destination].isnull().any():
            raise ValueError(
                f"Shipping costs for '{destination}' must be numeric."
            )

        if (cost_data[destination] < 0).any():
            raise ValueError(
                f"Shipping costs for '{destination}' cannot be negative."
            )

    # -----------------------------
    # VALIDATE SOURCE / DESTINATION MATCHING
    # -----------------------------
    supply_sources = set(supply_data["Source"])
    cost_sources = set(sources)

    missing_supply_sources = (
        cost_sources - supply_sources
    )

    extra_supply_sources = (
        supply_sources - cost_sources
    )

    if missing_supply_sources:
        raise ValueError(
            "The Supply file is missing source data for: "
            + ", ".join(sorted(missing_supply_sources))
        )

    if extra_supply_sources:
        raise ValueError(
            "The Supply file contains source names not found in the "
            "Transportation Cost file: "
            + ", ".join(sorted(extra_supply_sources))
        )

    demand_destinations = set(
        demand_data["Destination"]
    )

    cost_destinations = set(destinations)

    missing_demand_destinations = (
        cost_destinations - demand_destinations
    )

    extra_demand_destinations = (
        demand_destinations - cost_destinations
    )

    if missing_demand_destinations:
        raise ValueError(
            "The Demand file is missing destination data for: "
            + ", ".join(sorted(missing_demand_destinations))
        )

    if extra_demand_destinations:
        raise ValueError(
            "The Demand file contains destination names not found in the "
            "Transportation Cost file: "
            + ", ".join(sorted(extra_demand_destinations))
        )

    # -----------------------------
    # CREATE DICTIONARIES
    # -----------------------------
    shipping_cost = {
        (row["Source"], destination): row[destination]
        for _, row in cost_data.iterrows()
        for destination in destinations
    }

    supply = {
        row["Source"]: row["Supply"]
        for _, row in supply_data.iterrows()
    }

    demand = {
        row["Destination"]: row["Demand"]
        for _, row in demand_data.iterrows()
    }

    # -----------------------------
    # CHECK TOTAL FEASIBILITY
    # -----------------------------
    total_supply = sum(supply.values())
    total_demand = sum(demand.values())

    if total_supply < total_demand:
        raise ValueError(
            f"Total supply is {total_supply:,.0f}, but total demand is "
            f"{total_demand:,.0f}. Increase available supply or reduce demand "
            "before running the Transportation Optimizer."
        )

    # -----------------------------
    # VALIDATE CURRENT PLAN
    # -----------------------------
    for _, row in current_data.iterrows():
        if row["Source"] not in sources:
            raise ValueError(
                f"The Current Shipping Plan contains an unknown source: "
                f"{row['Source']}."
            )

        if row["Destination"] not in destinations:
            raise ValueError(
                f"The Current Shipping Plan contains an unknown destination: "
                f"{row['Destination']}."
            )

    current_source_totals = (
        current_data.groupby("Source")["Quantity"].sum()
    )

    for source, quantity in current_source_totals.items():
        if quantity > supply[source]:
            raise ValueError(
                f"The current shipping plan sends {quantity:,.0f} units from "
                f"{source}, but only {supply[source]:,.0f} units are available."
            )

    current_destination_totals = (
        current_data.groupby("Destination")["Quantity"].sum()
    )

    for destination in destinations:
        current_quantity = current_destination_totals.get(
            destination,
            0
        )

        if current_quantity != demand[destination]:
            raise ValueError(
                f"The current shipping plan sends {current_quantity:,.0f} units "
                f"to {destination}, but demand is {demand[destination]:,.0f}."
            )

    # -----------------------------
    # CREATE OPTIMIZATION MODEL
    # -----------------------------
    model = pulp.LpProblem(
        "Transportation_Optimizer",
        pulp.LpMinimize
    )

    # -----------------------------
    # DECISION VARIABLES
    # -----------------------------
    ship = pulp.LpVariable.dicts(
        "Ship",
        (sources, destinations),
        lowBound=0,
        cat="Continuous"
    )

    # -----------------------------
    # OBJECTIVE FUNCTION
    # -----------------------------
    model += pulp.lpSum(
        shipping_cost[(source, destination)]
        * ship[source][destination]
        for source in sources
        for destination in destinations
    )

    # -----------------------------
    # SUPPLY CONSTRAINTS
    # -----------------------------
    for source in sources:
        model += pulp.lpSum(
            ship[source][destination]
            for destination in destinations
        ) <= supply[source]

    # -----------------------------
    # DEMAND CONSTRAINTS
    # -----------------------------
    for destination in destinations:
        model += pulp.lpSum(
            ship[source][destination]
            for source in sources
        ) == demand[destination]

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
    current_total_cost = 0

    for _, row in current_data.iterrows():
        current_total_cost += (
            row["Quantity"]
            * shipping_cost[
                (row["Source"], row["Destination"])
            ]
        )

    # -----------------------------
    # BUILD OPTIMIZED RESULTS
    # -----------------------------
    shipment_rows = []

    for source in sources:
        for destination in destinations:
            optimized_quantity = pulp.value(
                ship[source][destination]
            )

            current_match = current_data[
                (current_data["Source"] == source)
                & (
                    current_data["Destination"]
                    == destination
                )
            ]

            if current_match.empty:
                current_quantity = 0
            else:
                current_quantity = (
                    current_match["Quantity"].sum()
                )

            change = (
                optimized_quantity
                - current_quantity
            )

            shipment_rows.append(
                {
                    "Source": source,
                    "Destination": destination,
                    "CurrentQuantity": current_quantity,
                    "OptimizedQuantity": optimized_quantity,
                    "Change": change,
                    "UnitCost":
                        shipping_cost[
                            (source, destination)
                        ]
                }
            )

    shipment_comparison = pd.DataFrame(
        shipment_rows
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
        "shipment_comparison":
            shipment_comparison,
        "current_total_cost":
            current_total_cost,
        "optimized_total_cost":
            optimized_total_cost,
        "savings":
            savings,
        "savings_percent":
            savings_percent
    }


# -----------------------------
# RUN DIRECTLY FOR TESTING
# -----------------------------
if __name__ == "__main__":
    results = run_transportation_optimizer()

    print("\nTransportation Optimizer")
    print("------------------------")

    print(f"Status: {results['status']}")

    print("\nShipment Changes:")

    for _, row in results[
        "shipment_comparison"
    ].iterrows():

        if row["Change"] != 0:
            print(
                f"{row['Source']} -> "
                f"{row['Destination']} | "
                f"Current: {row['CurrentQuantity']:,.0f} | "
                f"Optimized: {row['OptimizedQuantity']:,.0f} | "
                f"Change: {row['Change']:+,.0f}"
            )

    print(
        f"\nCurrent Transportation Cost: "
        f"${results['current_total_cost']:,.2f}"
    )

    print(
        f"Optimized Transportation Cost: "
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
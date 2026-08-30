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
    cost_data = pd.read_csv(cost_file)
    supply_data = pd.read_csv(supply_file)
    demand_data = pd.read_csv(demand_file)
    current_data = pd.read_csv(current_file)

    # -----------------------------
    # IDENTIFY SETS
    # -----------------------------
    sources = cost_data["Source"].tolist()

    destinations = [
        column
        for column in cost_data.columns
        if column != "Source"
    ]

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
    # VALIDATE CURRENT PLAN
    # -----------------------------
    required_current_columns = {
        "Source",
        "Destination",
        "Quantity"
    }

    missing_columns = (
        required_current_columns
        - set(current_data.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing current shipment columns: "
            + ", ".join(sorted(missing_columns))
        )

    current_data["Quantity"] = pd.to_numeric(
        current_data["Quantity"],
        errors="coerce"
    )

    if current_data["Quantity"].isnull().any():
        raise ValueError(
            "All current shipment quantities must be numeric."
        )

    for _, row in current_data.iterrows():
        if row["Source"] not in sources:
            raise ValueError(
                f"Unknown source in current plan: {row['Source']}"
            )

        if row["Destination"] not in destinations:
            raise ValueError(
                f"Unknown destination in current plan: "
                f"{row['Destination']}"
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
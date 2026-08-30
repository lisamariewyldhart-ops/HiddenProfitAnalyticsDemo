import pandas as pd
import pulp


def run_resource_allocation_optimizer(
    allocation_file="resource_allocation_data.csv",
    limits_file="resource_limits.csv"
):
    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    allocation_data = pd.read_csv(allocation_file)
    limits_data = pd.read_csv(limits_file)

    # -----------------------------
    # VALIDATE REQUIRED COLUMNS
    # -----------------------------
    required_columns = {
        "Initiative",
        "ProfitPerUnit",
        "BudgetPerUnit",
        "HoursPerUnit",
        "MaxUnits",
        "CurrentUnits"
    }

    missing_columns = (
        required_columns
        - set(allocation_data.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing allocation columns: "
            + ", ".join(sorted(missing_columns))
        )

    if not {"Resource", "Limit"}.issubset(
        limits_data.columns
    ):
        raise ValueError(
            "resource_limits.csv must contain "
            "Resource and Limit columns."
        )

    # -----------------------------
    # IDENTIFY INITIATIVES
    # -----------------------------
    initiatives = allocation_data[
        "Initiative"
    ].tolist()

    # -----------------------------
    # CONVERT NUMERIC COLUMNS
    # -----------------------------
    numeric_columns = [
        "ProfitPerUnit",
        "BudgetPerUnit",
        "HoursPerUnit",
        "MaxUnits",
        "CurrentUnits"
    ]

    for column in numeric_columns:
        allocation_data[column] = pd.to_numeric(
            allocation_data[column],
            errors="coerce"
        )

        if allocation_data[column].isnull().any():
            raise ValueError(
                f"All {column} values must be numeric."
            )

    limits_data["Limit"] = pd.to_numeric(
        limits_data["Limit"],
        errors="coerce"
    )

    if limits_data["Limit"].isnull().any():
        raise ValueError(
            "All resource limits must be numeric."
        )

    # -----------------------------
    # CREATE DICTIONARIES
    # -----------------------------
    profit_per_unit = {
        row["Initiative"]: row["ProfitPerUnit"]
        for _, row in allocation_data.iterrows()
    }

    budget_per_unit = {
        row["Initiative"]: row["BudgetPerUnit"]
        for _, row in allocation_data.iterrows()
    }

    hours_per_unit = {
        row["Initiative"]: row["HoursPerUnit"]
        for _, row in allocation_data.iterrows()
    }

    max_units = {
        row["Initiative"]: row["MaxUnits"]
        for _, row in allocation_data.iterrows()
    }

    current_units = {
        row["Initiative"]: row["CurrentUnits"]
        for _, row in allocation_data.iterrows()
    }

    resource_limits = {
        row["Resource"]: row["Limit"]
        for _, row in limits_data.iterrows()
    }

    if "Budget" not in resource_limits:
        raise ValueError(
            "Missing Budget resource limit."
        )

    if "StaffHours" not in resource_limits:
        raise ValueError(
            "Missing StaffHours resource limit."
        )

    budget_limit = resource_limits["Budget"]
    hours_limit = resource_limits["StaffHours"]

    # -----------------------------
    # VALIDATE CURRENT ALLOCATION
    # -----------------------------
    for initiative in initiatives:
        if current_units[initiative] < 0:
            raise ValueError(
                f"CurrentUnits cannot be negative for {initiative}."
            )

        if current_units[initiative] > max_units[initiative]:
            raise ValueError(
                f"CurrentUnits exceeds MaxUnits for {initiative}."
            )

    current_budget_used = sum(
        budget_per_unit[initiative]
        * current_units[initiative]
        for initiative in initiatives
    )

    current_hours_used = sum(
        hours_per_unit[initiative]
        * current_units[initiative]
        for initiative in initiatives
    )

    if current_budget_used > budget_limit:
        raise ValueError(
            "The current allocation exceeds the available budget."
        )

    if current_hours_used > hours_limit:
        raise ValueError(
            "The current allocation exceeds available staff hours."
        )

    # -----------------------------
    # CREATE OPTIMIZATION MODEL
    # -----------------------------
    model = pulp.LpProblem(
        "Resource_Allocation_Optimizer",
        pulp.LpMaximize
    )

    # -----------------------------
    # DECISION VARIABLES
    # -----------------------------
    units = pulp.LpVariable.dicts(
        "Units",
        initiatives,
        lowBound=0,
        cat="Integer"
    )

    # -----------------------------
    # OBJECTIVE FUNCTION
    # -----------------------------
    model += pulp.lpSum(
        profit_per_unit[initiative]
        * units[initiative]
        for initiative in initiatives
    )

    # -----------------------------
    # BUDGET CONSTRAINT
    # -----------------------------
    model += pulp.lpSum(
        budget_per_unit[initiative]
        * units[initiative]
        for initiative in initiatives
    ) <= budget_limit

    # -----------------------------
    # STAFF HOURS CONSTRAINT
    # -----------------------------
    model += pulp.lpSum(
        hours_per_unit[initiative]
        * units[initiative]
        for initiative in initiatives
    ) <= hours_limit

    # -----------------------------
    # MAXIMUM UNITS CONSTRAINTS
    # -----------------------------
    for initiative in initiatives:
        model += (
            units[initiative]
            <= max_units[initiative]
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
            f"No optimal allocation could be found. Status: {status}"
        )

    # -----------------------------
    # CURRENT BUSINESS RESULTS
    # -----------------------------
    current_profit = sum(
        profit_per_unit[initiative]
        * current_units[initiative]
        for initiative in initiatives
    )

    # -----------------------------
    # BUILD ALLOCATION COMPARISON
    # -----------------------------
    allocation_rows = []

    optimized_budget_used = 0
    optimized_hours_used = 0

    for initiative in initiatives:
        optimized_units = pulp.value(
            units[initiative]
        )

        optimized_budget = (
            optimized_units
            * budget_per_unit[initiative]
        )

        optimized_hours = (
            optimized_units
            * hours_per_unit[initiative]
        )

        optimized_budget_used += optimized_budget
        optimized_hours_used += optimized_hours

        allocation_rows.append(
            {
                "Initiative": initiative,
                "CurrentUnits":
                    current_units[initiative],
                "OptimizedUnits":
                    optimized_units,
                "Change":
                    optimized_units
                    - current_units[initiative],
                "ProfitPerUnit":
                    profit_per_unit[initiative],
                "CurrentProfit":
                    current_units[initiative]
                    * profit_per_unit[initiative],
                "OptimizedProfit":
                    optimized_units
                    * profit_per_unit[initiative]
            }
        )

    allocation_comparison = pd.DataFrame(
        allocation_rows
    )

    # -----------------------------
    # BUSINESS IMPACT
    # -----------------------------
    optimized_profit = pulp.value(
        model.objective
    )

    additional_profit = (
        optimized_profit
        - current_profit
    )

    improvement_percent = (
        (additional_profit / current_profit) * 100
        if current_profit > 0
        else 0
    )

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------
    return {
        "status": status,
        "allocation_comparison":
            allocation_comparison,
        "current_profit":
            current_profit,
        "optimized_profit":
            optimized_profit,
        "additional_profit":
            additional_profit,
        "improvement_percent":
            improvement_percent,
        "current_budget_used":
            current_budget_used,
        "optimized_budget_used":
            optimized_budget_used,
        "budget_limit":
            budget_limit,
        "current_hours_used":
            current_hours_used,
        "optimized_hours_used":
            optimized_hours_used,
        "hours_limit":
            hours_limit
    }


# -----------------------------
# RUN DIRECTLY FOR TESTING
# -----------------------------
if __name__ == "__main__":
    results = run_resource_allocation_optimizer()

    print("\nResource Allocation Optimizer")
    print("-----------------------------")

    print(f"Status: {results['status']}")

    print("\nAllocation Changes:")

    for _, row in results[
        "allocation_comparison"
    ].iterrows():

        print(
            f"{row['Initiative']} | "
            f"Current: {row['CurrentUnits']:,.0f} | "
            f"Optimized: {row['OptimizedUnits']:,.0f} | "
            f"Change: {row['Change']:+,.0f}"
        )

    print(
        f"\nCurrent Profit: "
        f"${results['current_profit']:,.2f}"
    )

    print(
        f"Optimized Profit: "
        f"${results['optimized_profit']:,.2f}"
    )

    print(
        f"Additional Profit Opportunity: "
        f"${results['additional_profit']:,.2f}"
    )

    print(
        f"Improvement Percentage: "
        f"{results['improvement_percent']:.2f}%"
    )

    print(
        f"\nCurrent Budget Used: "
        f"${results['current_budget_used']:,.2f} "
        f"of ${results['budget_limit']:,.2f}"
    )

    print(
        f"Optimized Budget Used: "
        f"${results['optimized_budget_used']:,.2f} "
        f"of ${results['budget_limit']:,.2f}"
    )

    print(
        f"Current Staff Hours Used: "
        f"{results['current_hours_used']:,.0f} "
        f"of {results['hours_limit']:,.0f}"
    )

    print(
        f"Optimized Staff Hours Used: "
        f"{results['optimized_hours_used']:,.0f} "
        f"of {results['hours_limit']:,.0f}"
    )
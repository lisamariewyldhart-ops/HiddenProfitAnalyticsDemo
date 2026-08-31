import pandas as pd
import pulp


def run_resource_allocation_optimizer(
    allocation_file="resource_allocation_data.csv",
    limits_file="resource_limits.csv"
):

    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    try:
        allocation_data = pd.read_csv(allocation_file)
        limits_data = pd.read_csv(limits_file)

    except pd.errors.EmptyDataError:
        raise ValueError(
            "One of the Resource Allocation CSV files is empty. "
            "Please use the downloadable Resource Allocation templates."
        )

    except pd.errors.ParserError:
        raise ValueError(
            "One of the Resource Allocation CSV files could not be read correctly. "
            "Please make sure both files are valid CSV files."
        )

    if allocation_data.empty:
        raise ValueError(
            "The Resource Allocation file does not contain any initiative data."
        )

    if limits_data.empty:
        raise ValueError(
            "The Resource Limits file does not contain any resource limits."
        )

    allocation_data.columns = allocation_data.columns.str.strip()
    limits_data.columns = limits_data.columns.str.strip()

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
            "Your Resource Allocation file is missing the required column(s): "
            + ", ".join(sorted(missing_columns))
            + ". Please use the downloadable Resource Allocation template "
            "and keep the column names exactly as shown."
        )

    required_limit_columns = {
        "Resource",
        "Limit"
    }

    missing_limit_columns = (
        required_limit_columns
        - set(limits_data.columns)
    )

    if missing_limit_columns:
        raise ValueError(
            "Your Resource Limits file is missing the required column(s): "
            + ", ".join(sorted(missing_limit_columns))
            + ". Please use the downloadable Resource Limits template "
            "and keep the column names exactly as shown."
        )

    # -----------------------------
    # CLEAN TEXT FIELDS
    # -----------------------------
    allocation_data["Initiative"] = (
        allocation_data["Initiative"]
        .astype(str)
        .str.strip()
    )

    limits_data["Resource"] = (
        limits_data["Resource"]
        .astype(str)
        .str.strip()
    )

    if (allocation_data["Initiative"] == "").any():
        raise ValueError(
            "Initiative names cannot be blank."
        )

    if (limits_data["Resource"] == "").any():
        raise ValueError(
            "Resource names cannot be blank."
        )

    # -----------------------------
    # CHECK DUPLICATES
    # -----------------------------
    if allocation_data["Initiative"].duplicated().any():
        raise ValueError(
            "Duplicate initiative names were found in the "
            "Resource Allocation file."
        )

    if limits_data["Resource"].duplicated().any():
        raise ValueError(
            "Duplicate resource names were found in the "
            "Resource Limits file."
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
    # VALIDATE BUSINESS VALUES
    # -----------------------------
    if (allocation_data["ProfitPerUnit"] < 0).any():
        raise ValueError(
            "ProfitPerUnit values cannot be negative."
        )

    if (allocation_data["BudgetPerUnit"] < 0).any():
        raise ValueError(
            "BudgetPerUnit values cannot be negative."
        )

    if (allocation_data["HoursPerUnit"] < 0).any():
        raise ValueError(
            "HoursPerUnit values cannot be negative."
        )

    if (allocation_data["MaxUnits"] < 0).any():
        raise ValueError(
            "MaxUnits values cannot be negative."
        )

    if (allocation_data["CurrentUnits"] < 0).any():
        raise ValueError(
            "CurrentUnits values cannot be negative."
        )

    if (limits_data["Limit"] < 0).any():
        raise ValueError(
            "Resource limits cannot be negative."
        )

    # MaxUnits and CurrentUnits must be whole numbers because
    # the optimization model uses integer decision variables.
    if not (
        allocation_data["MaxUnits"] % 1 == 0
    ).all():
        raise ValueError(
            "MaxUnits values must be whole numbers."
        )

    if not (
        allocation_data["CurrentUnits"] % 1 == 0
    ).all():
        raise ValueError(
            "CurrentUnits values must be whole numbers."
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

    # -----------------------------
    # VALIDATE REQUIRED RESOURCES
    # -----------------------------
    if "Budget" not in resource_limits:
        raise ValueError(
            "Your Resource Limits file is missing the Budget resource."
        )

    if "StaffHours" not in resource_limits:
        raise ValueError(
            "Your Resource Limits file is missing the StaffHours resource."
        )

    budget_limit = resource_limits["Budget"]
    hours_limit = resource_limits["StaffHours"]

    # -----------------------------
    # VALIDATE CURRENT ALLOCATION
    # -----------------------------
    for initiative in initiatives:
        if current_units[initiative] > max_units[initiative]:
            raise ValueError(
                f"CurrentUnits for {initiative} is "
                f"{current_units[initiative]:g}, but its MaxUnits is only "
                f"{max_units[initiative]:g}."
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
            f"The current allocation uses ${current_budget_used:,.2f} "
            f"of budget, but the available budget is only "
            f"${budget_limit:,.2f}."
        )

    if current_hours_used > hours_limit:
        raise ValueError(
            f"The current allocation uses {current_hours_used:g} staff hours, "
            f"but only {hours_limit:g} staff hours are available."
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
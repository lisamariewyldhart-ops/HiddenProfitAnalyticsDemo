import pandas as pd
from scipy.optimize import linprog


def classify_margin(margin):
    if margin >= 25:
        return "Strong"
    elif margin >= 18:
        return "Average"
    else:
        return "Needs Attention"


def optimize_profit_improvement(
    profit_gap,
    revenue_cost,
    expense_cost,
    max_revenue_increase,
    max_expense_reduction
):
    c = [
        revenue_cost,
        expense_cost
    ]

    # x + y >= profit_gap
    A_ub = [
        [-1, -1]
    ]

    b_ub = [
        -profit_gap
    ]

    bounds = [
        (0, max_revenue_increase),
        (0, max_expense_reduction)
    ]

    result = linprog(
        c,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        method="highs"
    )

    return result


def analyze_business(data, target_margin):
    data = data.copy()

    data["Profit"] = (
        data["Revenue"] - data["Expenses"]
    )

    data["Profit Margin"] = (
        data["Profit"] / data["Revenue"]
    ) * 100

    data["Profit Margin"] = (
        data["Profit Margin"].round(2)
    )

    data["Performance"] = (
        data["Profit Margin"].apply(classify_margin)
    )

    data["Target Profit"] = (
        data["Revenue"] * target_margin
    )

    data["Profit Opportunity"] = (
        data["Target Profit"] - data["Profit"]
    )

    data["Profit Opportunity"] = (
        data["Profit Opportunity"].clip(lower=0)
    )

    data["Profit Opportunity"] = (
        data["Profit Opportunity"].round(2)
    )

    return data


def validate_financial_data(data):

    required_columns = [
        "Month",
        "Revenue",
        "Expenses"
    ]

    # Empty file / no data rows
    if data.empty:
        return False, (
            "The uploaded CSV does not contain any financial data rows."
        )

    # Missing required columns
    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        return False, (
            "Missing required column(s): "
            + ", ".join(missing_columns)
            + ". The CSV must include Month, Revenue, and Expenses."
        )

    # Blank values
    if data[required_columns].isnull().any().any():
        return False, (
            "The financial data contains blank values. "
            "Please complete all Month, Revenue, and Expenses fields."
        )

    # Clean month names
    data["Month"] = (
        data["Month"]
        .astype(str)
        .str.strip()
    )

    # Blank month names
    if data["Month"].eq("").any():
        return False, (
            "Month names cannot be blank."
        )

    # Duplicate month names
    if data["Month"].duplicated().any():
        duplicate_months = (
            data.loc[
                data["Month"].duplicated(),
                "Month"
            ]
            .unique()
            .tolist()
        )

        return False, (
            "Duplicate month entries were found: "
            + ", ".join(duplicate_months)
            + ". Each month should appear only once."
        )

    # Revenue and Expenses must be numeric
    try:
        data["Revenue"] = pd.to_numeric(
            data["Revenue"]
        )

        data["Expenses"] = pd.to_numeric(
            data["Expenses"]
        )

    except (ValueError, TypeError):
        return False, (
            "Revenue and Expenses must contain numbers only."
        )

    # Negative revenue
    if (data["Revenue"] < 0).any():
        return False, (
            "Revenue cannot contain negative values."
        )

    # Negative expenses
    if (data["Expenses"] < 0).any():
        return False, (
            "Expenses cannot contain negative values."
        )

    # Revenue must be greater than zero
    if (data["Revenue"] == 0).any():
        return False, (
            "Revenue must be greater than zero for every period "
            "so profit margin can be calculated."
        )

    return True, ""
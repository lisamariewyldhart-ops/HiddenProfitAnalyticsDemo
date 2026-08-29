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

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        print()
        print("===== DATA ERROR =====")
        print(
            "Missing required column(s): "
            + ", ".join(missing_columns)
        )
        return False

    if data[required_columns].isnull().any().any():
        print()
        print("===== DATA ERROR =====")
        print("The financial data contains blank values.")
        return False

    try:
        data["Revenue"] = pd.to_numeric(
            data["Revenue"]
        )

        data["Expenses"] = pd.to_numeric(
            data["Expenses"]
        )

    except ValueError:
        print()
        print("===== DATA ERROR =====")
        print(
            "Revenue and Expenses must contain numbers only."
        )
        return False

    if (data["Revenue"] < 0).any():
        print()
        print("===== DATA ERROR =====")
        print("Revenue cannot contain negative values.")
        return False

    if (data["Expenses"] < 0).any():
        print()
        print("===== DATA ERROR =====")
        print("Expenses cannot contain negative values.")
        return False

    if (data["Revenue"] == 0).any():
        print()
        print("===== DATA ERROR =====")
        print(
            "Revenue must be greater than zero "
            "for every period."
        )
        return False

    if (
        data["Month"]
        .astype(str)
        .str.strip()
        .eq("")
        .any()
    ):
        print()
        print("===== DATA ERROR =====")
        print("Month names cannot be blank.")
        return False

    print()
    print("Financial data validation passed.")

    return True

from report_generator import (
    create_pdf_report,
    create_profit_opportunity_chart,
    create_scenario_cost_chart
)
from hidden_profit_engine import (
    analyze_business,
    optimize_profit_improvement,
    validate_financial_data
)
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

def setup_client():
    print()
    print("===== CLIENT SETUP =====")
    print()

    company_name = input("Company Name: ").strip()

    while True:
        try:
            target_percent = float(
                input("Target Profit Margin (%): ")
            )

            if 0 < target_percent < 100:
                break

            print("Please enter a percentage between 0 and 100.")

        except ValueError:
            print("Please enter a number, such as 22.")

    target_margin = target_percent / 100

    config_data = pd.DataFrame({
        "Setting": [
            "Company Name",
            "Target Profit Margin"
        ],
        "Value": [
            company_name,
            target_margin
        ]
    })

    config_data.to_csv(
        "client_config.csv",
        index=False
    )

    print()
    print("Client configuration saved.")
    print(f"Company: {company_name}")
    print(f"Target Profit Margin: {target_percent:.0f}%")

    return company_name, target_margin

def get_financial_data():
    print()
    print("===== FINANCIAL DATA =====")
    print()
    print("1. Enter new client financial data")
    print("2. Use existing financial data")
    print()

    while True:
        choice = input("Choose an option (1 or 2): ").strip()

        if choice in ["1", "2"]:
            break

        print("Please enter 1 or 2.")

    # ---------------------------------
    # OPTION 1: Enter new financial data
    # ---------------------------------
    if choice == "1":

        financial_records = []

        print()
        print("Enter monthly revenue and expenses.")
        print()

        while True:

            month = input("Month: ").strip()

            # Revenue
            while True:
                try:
                    revenue = float(
                        input("Revenue: $").replace(",", "")
                    )

                    if revenue >= 0:
                        break

                    print("Revenue cannot be negative.")

                except ValueError:
                    print(
                        "Please enter a valid number, such as 42000."
                    )

            # Expenses
            while True:
                try:
                    expenses = float(
                        input("Expenses: $").replace(",", "")
                    )

                    if expenses >= 0:
                        break

                    print("Expenses cannot be negative.")

                except ValueError:
                    print(
                        "Please enter a valid number, such as 35000."
                    )

            financial_records.append({
                "Month": month,
                "Revenue": revenue,
                "Expenses": expenses
            })

            print()

            another = input(
                "Add another month? (y/n): "
            ).strip().lower()

            if another != "y":
                break

            print()

        data = pd.DataFrame(financial_records)

        data.to_csv(
            "monthly_revenue.csv",
            index=False
        )

        print()
        print("Financial data saved to monthly_revenue.csv")

        return data

    # ---------------------------------
    # OPTION 2: Use existing CSV
    # ---------------------------------
    else:

        try:
            data = pd.read_csv("monthly_revenue.csv")

            print()
            print("Existing financial data loaded.")
            print()
            print(data)

            return data

        except FileNotFoundError:
            print()
            print("monthly_revenue.csv was not found.")
            print(
                "Please run the program again and choose option 1."
            )

            return None

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

def main():
    company_name, target_margin = setup_client()

    data = get_financial_data()

    if data is None:
        return

    if not validate_financial_data(data):
        print()
        print("Analysis stopped because the financial data is invalid.")
        return

    data = analyze_business(
        data,
        target_margin
    )

    data = analyze_business(data, target_margin)

    total_revenue = data["Revenue"].sum()
    total_profit = data["Profit"].sum()
    total_opportunity = data["Profit Opportunity"].sum()
    largest_opportunity_index = data["Profit Opportunity"].idxmax()
    largest_opportunity = data.loc[largest_opportunity_index]

    profit_gap = largest_opportunity["Profit Opportunity"]

    revenue_cost = 0.30
    expense_cost = 0.10

    feasible_scenarios = []

    scenarios = pd.read_csv("scenarios.csv")
    
    max_revenue_increase = 3000
    max_expense_reduction = 1000
    optimization_result = optimize_profit_improvement(
        profit_gap,
        revenue_cost,
        expense_cost,
        max_revenue_increase,
        max_expense_reduction
)

    print()
    print("===== HIDDEN PROFIT ANALYSIS =====")
    print()
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Profit: ${total_profit:,.2f}")
    print(
    f"Total Hidden Profit Opportunity: "
    f"${total_opportunity:,.2f}"
    )
    print(
    f"Largest Profit Opportunity: "
    f"{largest_opportunity['Month']} "
    f"(${largest_opportunity['Profit Opportunity']:,.2f})"
    )
    print(
    f"Priority: {largest_opportunity['Month']} has the largest "
    f"gap to the {target_margin * 100:.0f}% target margin."
    )
    print()
    print("Monthly Analysis:")
    print(
        data[
            [
                "Month",
                "Revenue",
                "Expenses",
                "Profit",
                "Profit Margin",
                "Performance",
                "Profit Opportunity"
            ]
        ]
    )
    if optimization_result.success:
        additional_revenue = optimization_result.x[0]
        expense_reduction = optimization_result.x[1]
        implementation_cost = optimization_result.fun

        print()
        print("===== RECOMMENDED ACTION PLAN =====")
        print(f"Priority Month: {largest_opportunity['Month']}")
        print(f"Profit Gap: ${profit_gap:,.2f}")
        print(f"Recommended Revenue Increase: ${additional_revenue:,.2f}")
        print(f"Recommended Expense Reduction: ${expense_reduction:,.2f}")
        print(f"Estimated Implementation Cost: ${implementation_cost:,.2f}")
    else:
        max_possible_improvement = (
            max_revenue_increase + max_expense_reduction
        )

        remaining_gap = (
            profit_gap - max_possible_improvement
        )

        print()
        print("===== OPTIMIZATION ALERT =====")
        print("No feasible optimization plan was found.")
        print(f"Required Profit Improvement: ${profit_gap:,.2f}")
        print(
            f"Maximum Possible Improvement: "
            f"${max_possible_improvement:,.2f}"
        )
        print(f"Remaining Unresolved Gap: ${remaining_gap:,.2f}")
        additional_expense_capacity_needed = remaining_gap

        print(
            f"Recommended Constraint Adjustment: "
            f"Increase allowable expense reduction by at least "
            f"${additional_expense_capacity_needed:,.2f}."
            )
    print()
    print("===== SCENARIO ANALYSIS =====")

    scenario_results = []

    for _, row in scenarios.iterrows():
        scenario_name = row["Scenario"]
        max_revenue_increase = row["Max Revenue Increase"]
        max_expense_reduction = row["Max Expense Reduction"]
        revenue_cost = row["Revenue Cost"]
        expense_cost = row["Expense Cost"]

        scenario_result = optimize_profit_improvement(
            profit_gap,
            revenue_cost,
            expense_cost,
            max_revenue_increase,
            max_expense_reduction
        )
        print()
        print(f"Scenario: {scenario_name}")

        if scenario_result.success:
            scenario_revenue = scenario_result.x[0]
            scenario_expense = scenario_result.x[1]
            scenario_cost = scenario_result.fun
            scenario_results.append({
                "Scenario": scenario_name,
                "Status": "Feasible",
                "Revenue Increase": scenario_revenue,
                "Expense Reduction": scenario_expense,
                "Implementation Cost": scenario_cost,
                "Remaining Gap": 0
        })

            print("Status: Feasible")
            print(
                f"Revenue Increase: "
                f"${scenario_revenue:,.2f}"
            )
            print(
                f"Expense Reduction: "
                f"${scenario_expense:,.2f}"
            )
            print(
                f"Implementation Cost: "
                f"${scenario_cost:,.2f}"
            )

        else:
            max_improvement = (
                max_revenue_increase + max_expense_reduction
            )

            scenario_gap = (
                profit_gap - max_improvement
            )

            scenario_results.append({
                "Scenario": scenario_name,
                "Status": "Infeasible",
                "Revenue Increase": 0,
                "Expense Reduction": 0,
                "Implementation Cost": 0,
                "Remaining Gap": scenario_gap
            })

            print("Status: Infeasible")
            print(
                f"Remaining Gap: "
                f"${scenario_gap:,.2f}"
            )


    # The for loop is finished here
    scenario_results_df = pd.DataFrame(scenario_results)
    scenario_results_df.to_csv(
        "scenario_results.csv",
        index=False
    )

    print()
    print("Scenario results saved to scenario_results.csv")

    feasible_results = scenario_results_df[
        scenario_results_df["Status"] == "Feasible"
    ]

    if not feasible_results.empty:
        best_index = feasible_results["Implementation Cost"].idxmin()
        best_scenario = feasible_results.loc[best_index]

        print()
        print("===== BEST SCENARIO =====")
        print(f"Scenario: {best_scenario['Scenario']}")
        print(
            f"Recommended Revenue Increase: "
            f"${best_scenario['Revenue Increase']:,.2f}"
        )
        print(
            f"Recommended Expense Reduction: "
            f"${best_scenario['Expense Reduction']:,.2f}"
        )
        print(
            f"Minimum Implementation Cost: "
            f"${best_scenario['Implementation Cost']:,.2f}"
        )

        executive_summary = (
            f"{largest_opportunity['Month']} represents the largest "
            f"hidden profit opportunity at "
            f"${largest_opportunity['Profit Opportunity']:,.2f}.\n\n"

            f"The {best_scenario['Scenario']} scenario provides the "
            f"lowest-cost feasible strategy for closing this profit gap.\n\n"

            f"This strategy recommends generating "
            f"${best_scenario['Revenue Increase']:,.2f} in additional revenue "
            f"and reducing expenses by "
            f"${best_scenario['Expense Reduction']:,.2f}.\n\n"

            f"The estimated implementation cost is "
            f"${best_scenario['Implementation Cost']:,.2f}."
        )

        print()
        print("===== EXECUTIVE SUMMARY =====")
        print()
        print(executive_summary)

        with open("executive_summary.txt", "w") as file:
            file.write(
                "HIDDEN PROFIT ANALYTICS - EXECUTIVE SUMMARY\n\n"
            )
            file.write(executive_summary)

        print()
        print("Executive summary saved to executive_summary.txt")

    else:
        print()
        print("No feasible scenarios were found.")

        # ==========================================
    # CHART 1: HIDDEN PROFIT OPPORTUNITY
    # ==========================================

    print()
    print("Creating profit opportunity chart...")

    create_profit_opportunity_chart(
        data,
        largest_opportunity
    )


    # ==========================================
    # CHART 2: SCENARIO IMPLEMENTATION COST
    # ==========================================

    print()
    print("Creating scenario comparison chart...")

    create_scenario_cost_chart(
        scenario_results_df,
        best_scenario
    )

    create_pdf_report(
        data,
        total_revenue,
        total_profit,
        total_opportunity,
        largest_opportunity,
        best_scenario,
        company_name,
        target_margin
    )    

if __name__ == "__main__":
    main()
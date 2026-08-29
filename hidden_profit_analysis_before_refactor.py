import pandas as pd
from scipy.optimize import linprog
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

    c = [revenue_cost, expense_cost]

    # Profit improvement constraint:
    # x + y >= profit_gap
    A_ub = [
        [-1, -1]
    ]

    b_ub = [
        -profit_gap
    ]

    # Maximum feasible improvements
    bounds = [
        (0, max_revenue_increase),  # additional revenue
        (0, max_expense_reduction)   # expense reduction
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
    data["Profit"] = data["Revenue"] - data["Expenses"]

    data["Profit Margin"] = (
        data["Profit"] / data["Revenue"]
    ) * 100

    data["Profit Margin"] = data["Profit Margin"].round(2)

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

    data["Profit Opportunity"] = data["Profit Opportunity"].round(2)
    return data

def create_pdf_report(
    data,
    total_revenue,
    total_profit,
    total_opportunity,
    largest_opportunity,
    best_scenario,
    company_name,
    target_margin
):
    pdf_name = "hidden_profit_report.pdf"

    doc = SimpleDocTemplate(
        pdf_name,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(
    Paragraph(
        "Hidden Profit Analytics",
        styles["Title"]
    )
    )

    story.append(
        Paragraph(
            f"{company_name} - Business Optimization Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 0.20 * inch))

    # Executive Summary
    story.append(
        Paragraph(
            "Executive Summary",
            styles["Heading2"]
        )
    )

    summary_text = (
        f"{largest_opportunity['Month']} represents the largest "
        f"hidden profit opportunity at "
        f"${largest_opportunity['Profit Opportunity']:,.2f}. "
        f"The {best_scenario['Scenario']} scenario provides the "
        f"lowest-cost feasible strategy for closing this profit gap. "
        f"The recommended strategy calls for "
        f"${best_scenario['Revenue Increase']:,.2f} in additional revenue "
        f"and ${best_scenario['Expense Reduction']:,.2f} in expense reduction, "
        f"with an estimated implementation cost of "
        f"${best_scenario['Implementation Cost']:,.2f}."
    )

    story.append(
        Paragraph(
            summary_text,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    # Key Metrics
    story.append(
        Paragraph(
            "Key Financial Metrics",
            styles["Heading2"]
        )
    )
    metrics_data = [
            ["Metric", "Value"],
            [
                "Total Revenue",
                f"${total_revenue:,.2f}"
            ],
            [
                "Total Profit",
                f"${total_profit:,.2f}"
            ],
            [
                "Target Profit Margin",
                f"{target_margin * 100:.0f}%"
            ],
            [
                "Total Hidden Profit Opportunity",
                f"${total_opportunity:,.2f}"
            ],
            [
                "Largest Opportunity",
                f"{largest_opportunity['Month']} "
                f"(${largest_opportunity['Profit Opportunity']:,.2f})"
            ],
            [
                "Recommended Scenario",
                best_scenario["Scenario"]
            ]
        ]
    metrics_table = Table(
        metrics_data,
        colWidths=[3.5 * inch, 3.0 * inch]
    )

    metrics_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(metrics_table)
    story.append(Spacer(1, 0.3 * inch))

    # Monthly Analysis Table
    story.append(
        Paragraph(
            "Monthly Opportunity Analysis",
            styles["Heading2"]
        )
    )

    monthly_table_data = [
        [
            "Month",
            "Revenue",
            "Expenses",
            "Profit",
            "Margin",
            "Performance",
            "Opportunity"
        ]
    ]

    for _, row in data.iterrows():
        monthly_table_data.append([
            row["Month"],
            f"${row['Revenue']:,.0f}",
            f"${row['Expenses']:,.0f}",
            f"${row['Profit']:,.0f}",
            f"{row['Profit Margin']:.2f}%",
            row["Performance"],
            f"${row['Profit Opportunity']:,.0f}"
        ])

    monthly_table = Table(
        monthly_table_data,
        repeatRows=1
    )

    monthly_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 1), (4, -1), "RIGHT"),
            ("ALIGN", (6, 1), (6, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    story.append(monthly_table)
    story.append(PageBreak())

    # Charts
    story.append(
        Paragraph(
            "Profit Opportunity by Month",
            styles["Heading2"]
        )
    )

    story.append(
        Image(
            "profit_opportunity.png",
            width=5.8 * inch,
            height=3.3 * inch
        )
    )

    story.append(Spacer(1, 0.08 * inch))

    story.append(
        Paragraph(
            "Scenario Cost Comparison",
            styles["Heading2"]
        )
    )

    story.append(
        Image(
            "scenario_cost_comparison.png",
            width=5.0 * inch,
            height=3.1 * inch
        )
    )

    # Recommendation
    story.append(
        Paragraph(
            "Recommended Strategy",
            styles["Heading2"]
        )
    )

    recommendation_data = [
        ["Recommendation", "Amount"],
        [
            "Revenue Increase",
            f"${best_scenario['Revenue Increase']:,.2f}"
        ],
        [
            "Expense Reduction",
            f"${best_scenario['Expense Reduction']:,.2f}"
        ],
        [
            "Implementation Cost",
            f"${best_scenario['Implementation Cost']:,.2f}"
        ]
    ]

    recommendation_table = Table(
        recommendation_data,
        colWidths=[3.5 * inch, 2.5 * inch]
    )

    recommendation_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(recommendation_table)

    story.append(Spacer(1, 0.15 * inch))

    business_impact = (
        f"<b>Business Impact:</b> The recommended "
        f"{best_scenario['Scenario']} strategy closes "
        f"{largest_opportunity['Month']}'s "
        f"${largest_opportunity['Profit Opportunity']:,.2f} profit gap "
        f"at the lowest estimated implementation cost. "
        f"The model recommends "
        f"${best_scenario['Expense Reduction']:,.2f} in expense reduction "
        f"and ${best_scenario['Revenue Increase']:,.2f} in additional revenue."
    )

    story.append(
        Paragraph(
            business_impact,
            styles["BodyText"]
        )
    )

    doc.build(story)

    print()
    print(f"PDF report saved to {pdf_name}")

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
    required_columns = ["Month", "Revenue", "Expenses"]

    # Check required columns
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

    # Check for blank values
    if data[required_columns].isnull().any().any():
        print()
        print("===== DATA ERROR =====")
        print(
            "The financial data contains blank values."
        )
        return False

    # Make sure revenue and expenses are numeric
    try:
        data["Revenue"] = pd.to_numeric(data["Revenue"])
        data["Expenses"] = pd.to_numeric(data["Expenses"])

    except ValueError:
        print()
        print("===== DATA ERROR =====")
        print(
            "Revenue and Expenses must contain numbers only."
        )
        return False

    # Check for negative values
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

    # Prevent division by zero when calculating margin
    if (data["Revenue"] == 0).any():
        print()
        print("===== DATA ERROR =====")
        print(
            "Revenue must be greater than zero for every period."
        )
        return False

    # Check blank month names
    if data["Month"].astype(str).str.strip().eq("").any():
        print()
        print("===== DATA ERROR =====")
        print("Month names cannot be blank.")
        return False

    print()
    print("Financial data validation passed.")

    return True       

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

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        data["Month"],
        data["Profit Opportunity"]
    )

    plt.title("Hidden Profit Opportunity by Month")
    plt.xlabel("Month")
    plt.ylabel("Profit Opportunity ($)")

    # Add dollar values above each bar
    for bar in bars:
        height = bar.get_height()

        plt.annotate(
            f"${height:,.0f}",
            xy=(
                bar.get_x() + bar.get_width() / 2,
                height
            ),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom"
        )

    # Add priority label
    priority_month = largest_opportunity["Month"]
    priority_value = largest_opportunity["Profit Opportunity"]

    plt.annotate(
        f"Priority: {priority_month}",
        xy=(priority_month, priority_value),
        xytext=(0, -35),
        textcoords="offset points",
        ha="center",
        va="top"
    )

    plt.tight_layout()
    plt.savefig("profit_opportunity.png")
    plt.show()
    plt.close()


    # ==========================================
    # CHART 2: SCENARIO IMPLEMENTATION COST
    # ==========================================

    print()
    print("Creating scenario comparison chart...")

    feasible_chart_data = scenario_results_df[
        scenario_results_df["Status"] == "Feasible"
    ]

    if not feasible_chart_data.empty:

        plt.figure(figsize=(8, 6))

        scenario_bars = plt.bar(
            feasible_chart_data["Scenario"],
            feasible_chart_data["Implementation Cost"]
        )

        plt.title("Implementation Cost by Feasible Scenario")
        plt.xlabel("Scenario")
        plt.ylabel("Implementation Cost ($)")

        # Add dollar values above each bar
        for bar in scenario_bars:
            height = bar.get_height()

            plt.annotate(
                f"${height:,.0f}",
                xy=(
                    bar.get_x() + bar.get_width() / 2,
                    height
                ),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom"
            )

        # Add recommended scenario label
        recommended_scenario = best_scenario["Scenario"]
        recommended_cost = best_scenario["Implementation Cost"]

        plt.annotate(
            f"Recommended: {recommended_scenario}",
            xy=(recommended_scenario, recommended_cost),
            xytext=(0, -35),
            textcoords="offset points",
            ha="center",
            va="top"
        )

        plt.tight_layout()
        plt.savefig("scenario_cost_comparison.png")
        plt.show()
        plt.close()

    else:
        print("No feasible scenarios available for chart.")

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
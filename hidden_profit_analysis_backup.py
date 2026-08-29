import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

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

def analyze_business(data):
    data["Profit"] = data["Revenue"] - data["Expenses"]

    data["Profit Margin"] = (
        data["Profit"] / data["Revenue"]
    ) * 100

    data["Profit Margin"] = data["Profit Margin"].round(2)

    data["Performance"] = (
        data["Profit Margin"].apply(classify_margin)
    )

    target_margin = 0.25

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

def main():
    data = pd.read_csv("monthly_revenue.csv")

    data = analyze_business(data)

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
    f"gap to the 25% target margin."
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

if __name__ == "__main__":
    main()
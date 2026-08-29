# Hidden Profit Calculator - Version 2

def get_number(prompt):
    while True:
        try:
            number = float(input(prompt))
            return number
        except ValueError:
            print("Please enter a valid number.")


def calculate_profit_metrics(revenue, expenses):
    profit = revenue - expenses

    if revenue > 0:
        profit_margin = (profit / revenue) * 100
        expense_ratio = (expenses / revenue) * 100
    else:
        profit_margin = None
        expense_ratio = None

    return profit, profit_margin, expense_ratio

def display_results(revenue, expenses, profit, profit_margin, expense_ratio):
    print()
    print("----- RESULTS -----")
    print(f"Revenue: ${revenue:,.2f}")
    print(f"Expenses: ${expenses:,.2f}")
    print(f"Profit: ${profit:,.2f}")

    if profit_margin is not None:
        print(f"Profit Margin: {profit_margin:.1f}%")
        print(f"Expense Ratio: {expense_ratio:.1f}%")
    else:
        print("Profit Margin: N/A")
        print("Expense Ratio: N/A")

def analyze_profit_margin(profit_margin):
    if profit_margin is None:
        print("No profit margin analysis is available because revenue is zero.")

    elif profit_margin >= 30:
        print("Excellent! Your business has a strong profit margin.")

    elif profit_margin >= 15:
        print("Good job! Your business is profitable, but there may be opportunities to improve.")

    else:
        print("Warning: Your profit margin is low. There may be hidden profit opportunities.")

def main():
    revenue = get_number("Enter your revenue: $")
    expenses = get_number("Enter your expenses: $")

    profit, profit_margin, expense_ratio = calculate_profit_metrics(revenue, expenses)

    display_results(revenue, expenses, profit, profit_margin, expense_ratio)
    analyze_profit_margin(profit_margin)

if __name__ == "__main__":
    main()
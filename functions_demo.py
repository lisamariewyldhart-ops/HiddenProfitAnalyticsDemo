# Hidden Profit Analytics
# Lesson 2 - Functions


def calculate_profit(revenue, expenses):
    """Calculate business profit."""
    profit = revenue - expenses
    return profit


# Main program

revenue = float(input("Enter revenue: $"))
expenses = float(input("Enter expenses: $"))

profit = calculate_profit(revenue, expenses)

print()
print(f"Profit = ${profit:,.2f}")

# Tax calculation function

def calculate_tax(profit, tax_rate):
    """Calculate estimated tax."""
    tax = profit * tax_rate / 100
    return tax


tax_rate = float(input("Enter tax rate (%): "))

tax = calculate_tax(profit, tax_rate)

print()
print(f"Estimated Tax = ${tax:,.2f}")
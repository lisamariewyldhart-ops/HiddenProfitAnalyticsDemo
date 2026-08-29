from scipy.optimize import linprog

# Decision variables:
# x = additional revenue
# y = expense reduction

# Objective:
# Minimize 0.30x + 0.10y
c = [0.30, 0.10]

# Constraints:
# x + y >= 4250
# linprog uses <= constraints, so multiply by -1:
# -x - y <= -4250
A_ub = [
    [-1, -1]
]

b_ub = [
    -4250
]

# Bounds:
# 0 <= x <= 3000
# 0 <= y <= 2500
bounds = [
    (0, 3000),
    (0, 2500)
]

result = linprog(
    c,
    A_ub=A_ub,
    b_ub=b_ub,
    bounds=bounds,
    method="highs"
)

if result.success:
    additional_revenue = result.x[0]
    expense_reduction = result.x[1]
    minimum_cost = result.fun

    print()
    print("===== OPTIMAL PROFIT IMPROVEMENT PLAN =====")
    print(f"Additional Revenue: ${additional_revenue:,.2f}")
    print(f"Expense Reduction: ${expense_reduction:,.2f}")
    print(f"Minimum Implementation Cost: ${minimum_cost:,.2f}")
else:
    print("No optimal solution was found.")

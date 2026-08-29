import pandas as pd

# Simple pandas demo
sales_data = {
    "Product": ["A", "B", "A", "C", "B"],
    "Units": [10, 15, 5, 20, 12],
    "Revenue": [100, 180, 60, 220, 150],
}

df = pd.DataFrame(sales_data)
print("Original data:")
print(df)

# Filter rows
high_volume = df[df["Units"] > 10]
print("\nProducts with more than 10 units:")
print(high_volume)

# Aggregate by product
summary = (
    df.groupby("Product", as_index=False)
      .agg(Total_Units=("Units", "sum"), Total_Revenue=("Revenue", "sum"))
)
print("\nSummary by product:")
print(summary)

def classify_margin(margin):
    if margin >= 25:
        return "Strong"
    elif margin >= 18:
        return "Average"
    else:
        return "Needs Attention"
    
# Save to CSV for later use
output_path = "sales_summary.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved full dataset to {output_path}")
data = pd.read_csv("monthly_revenue.csv")
data["Profit"] = data["Revenue"] - data["Expenses"]
data["Profit Margin"] = (data["Profit"] / data["Revenue"]) * 100

data["Profit Margin"] = data["Profit Margin"].round(2)

data["Performance"] = data["Profit Margin"].apply(classify_margin)
print()
print("Monthly Profit Analysis:")
print(data)

print()
print("Revenue column:")
print(data["Revenue"])

total_revenue = data["Revenue"].sum()
average_revenue = data["Revenue"].mean()

print()
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Average Revenue: ${average_revenue:,.2f}")

highest_revenue = data["Revenue"].max()
lowest_revenue = data["Revenue"].min()

print(f"Highest Revenue: ${highest_revenue:,.2f}")
print(f"Lowest Revenue: ${lowest_revenue:,.2f}")

best_index = data["Revenue"].idxmax()
print()
best_month = data.loc[best_index]
print(f"Best Month: {best_month['Month']} (${best_month['Revenue']:,.2f})")
worst_index = data["Revenue"].idxmin()
print()
worst_month = data.loc[worst_index]
print(f"Worst Month: {worst_month['Month']} (${worst_month['Revenue']:,.2f})")
best_margin_index = data["Profit Margin"].idxmax()
best_margin = data.loc[best_margin_index]

worst_margin_index = data["Profit Margin"].idxmin()
worst_margin = data.loc[worst_margin_index]

print()
print(f"Best Profit Margin: {best_margin['Month']} ({best_margin['Profit Margin']:.2f}%)")
print(f"Worst Profit Margin: {worst_margin['Month']} ({worst_margin['Profit Margin']:.2f}%)")
performance_counts = data["Performance"].value_counts()

print()
print("Performance Summary:")
print(performance_counts)

performance_percent = data["Performance"].value_counts(normalize=True) * 100
print()
print("Performance Percentages:")
print(performance_percent)

needs_attention = data[data["Performance"] == "Needs Attention"]

print()
print("Months Needing Attention:")
print(needs_attention)

Strong = data[data["Performance"] == "Strong"]

print()
print("Months with Strong Performance:")
print(Strong)

target_margin = 0.25

data["Target Profit"] = data["Revenue"] * target_margin

data["Profit Opportunity"] = data["Target Profit"] - data["Profit"]

print()
print("Profit Opportunity Analysis:")
print(data[["Month", "Revenue", "Profit", "Profit Margin", "Target Profit", "Profit Opportunity"]])

data["Profit Opportunity"] = data["Profit Opportunity"].clip(lower=0)

data["Profit Opportunity"] = data["Profit Opportunity"].round(2)

total_opportunity = data["Profit Opportunity"].sum()

print()
print(f"Total Hidden Profit Opportunity: ${total_opportunity:,.2f}")

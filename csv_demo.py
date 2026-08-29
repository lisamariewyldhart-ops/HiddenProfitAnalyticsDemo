import csv

monthly_data = {}
revenues = []

with open("monthly_revenue.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        month = row["Month"]
        revenue = float(row["Revenue"])
        revenues.append(revenue)
        monthly_data[month] = revenue

        print(f"{month}: ${revenue:,.2f}")

total_revenue = sum(revenues)
average_revenue = total_revenue / len(revenues)
best_month = max(monthly_data, key=monthly_data.get)
worst_month = min(monthly_data, key=monthly_data.get)

print()
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Average Monthly Revenue: ${average_revenue:,.2f}")
print(f"Best Month: {best_month} (${monthly_data[best_month]:,.2f})")
print(f"Worst Month: {worst_month} (${monthly_data[worst_month]:,.2f})")

highest_revenue = max(revenues)
lowest_revenue = min(revenues)

print(f"Highest Revenue: ${highest_revenue:,.2f}")
print(f"Lowest Revenue: ${lowest_revenue:,.2f}")
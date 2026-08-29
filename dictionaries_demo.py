monthly_revenue = {
    "January": 42000,
    "February": 47500,
    "March": 51000,
    "April": 49000,
    "May": 56000
}

strong_count = 0
average_count = 0
attention_count = 0

total_months = len(monthly_revenue)

for month, revenue in monthly_revenue.items():
    print(f"{month}: ${revenue:,.2f}")

for month, revenue in monthly_revenue.items():
    if revenue >= 50000:
        print(f"{month}: Strong Month: ${revenue:,.2f}")
        strong_count += 1
    elif revenue >= 45000 and revenue <= 49999.99:
        print(f"{month}: Average Month: ${revenue:,.2f}")
        average_count += 1

    else:
        print(f"{month}: Needs Attention: ${revenue:,.2f}")
        attention_count += 1

strong_percent = (strong_count / total_months) * 100 if total_months > 0 else 0
average_percent = (average_count / total_months) * 100 if total_months > 0 else 0
attention_percent = (attention_count / total_months) * 100 if total_months > 0 else 0

print(f"Strong Months: {strong_count} ({strong_percent:.1f}%)")
print(f"Average Months: {average_count} ({average_percent:.1f}%)")
print(f"Months Needing Attention: {attention_count} ({attention_percent:.1f}%)")

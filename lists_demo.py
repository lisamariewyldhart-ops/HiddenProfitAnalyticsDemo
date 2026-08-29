monthly_revenue = [42000, 47500, 51000, 49000, 56000]

print(monthly_revenue)
print(monthly_revenue[0])
print(monthly_revenue[3])

total_revenue = sum(monthly_revenue)

print(f"Total Revenue: ${total_revenue:,.2f}")

average_revenue = total_revenue / len(monthly_revenue)

print(f"Average Monthly Revenue: ${average_revenue:,.2f}")

for revenue in monthly_revenue:
    print(f"Monthly Revenue: ${revenue:,.2f}")

for revenue in monthly_revenue:
    if revenue >= 50000:
        print(f"Strong Month: ${revenue:,.2f}")

    else:
        print(f"Needs Attention: ${revenue:,.2f}")
            
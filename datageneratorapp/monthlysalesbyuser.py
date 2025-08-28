
import pandas as pd
import matplotlib.pyplot as plt

sales_df = pd.read_csv('./data/salesdata_10000.csv', parse_dates=['sale_date'])
sales_df["month"] = sales_df["sale_date"].dt.to_period("M").astype(str)

monthly_sales = sales_df.groupby(['month', 'user_name'])["total_price"].sum().reset_index()

print(monthly_sales.head(5))
monthly_sales["month"] = monthly_sales["month"]

# Pivot the data: rows = months, columns = user_name, values = total_price
pivot_df = monthly_sales.pivot(index="month", columns="user_name", values="total_price")

print(pivot_df.head(5))

# Plot
plt.figure(figsize=(12, 6))
for username in pivot_df.columns:
    plt.plot(pivot_df.index, pivot_df[username], label=username, marker='o')


# Formatting
plt.title("Monthly Sales by username")
plt.xlabel("Month")
plt.ylabel("Total Price")
plt.legend(title="Username")
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)

plt.show()
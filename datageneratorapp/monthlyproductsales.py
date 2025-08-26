import pandas as pd
import matplotlib.pyplot as plt

sales_df = pd.read_csv('./salesdata_10000.csv', parse_dates=['sale_date'])
sales_df["month"] = sales_df["sale_date"].dt.to_period("M").astype(str)

monthly_sales = sales_df.groupby(['month', 'product_name'])["total_price"].sum().reset_index()

print(monthly_sales.head(5))
monthly_sales["month"] = monthly_sales["month"]

# Pivot the data: rows = months, columns = product_name, values = total_price
pivot_df = monthly_sales.pivot(index="month", columns="product_name", values="total_price")

print(pivot_df.head(5))


# Plot
plt.figure(figsize=(12, 6))
for product in pivot_df.columns:
    plt.plot(pivot_df.index, pivot_df[product], label=product, marker='o')


# Formatting
plt.title("Monthly Sales by Product")
plt.xlabel("Month")
plt.ylabel("Total Price")
plt.legend(title="Product Name")
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)

plt.show()
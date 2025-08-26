import pandas as pd
import matplotlib.pyplot as plt

sales_df = pd.read_csv('./salesdata_10000.csv', parse_dates=['sale_date'])
sales_df["month"] = sales_df["sale_date"].dt.to_period("M")


monthly_sales = sales_df.groupby("month")["total_price"].sum().reset_index()

print(monthly_sales.head(5))

monthly_sales.plot(x='month', y='total_price', kind='line')
plt.title('Monthly Sales Over Time')
plt.xlabel('Month')
plt.ylabel('Total Sales ($)')
plt.grid(True)
plt.show()




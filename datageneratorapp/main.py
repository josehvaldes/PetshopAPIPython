import pandas as pd
import random
from faker import Faker
import datetime

# Initialize Faker for creating fake data
fake = Faker()

#Generation
num_records = 10000
sales_data = []

products_df = pd.read_csv('./input/productsdata.csv')
clients_df = pd.read_csv('./input/clientsdata.csv')
users_df = pd.read_csv('./input/usersdata.csv')

print ('Generating sales data...') 

for _ in range(num_records):
    product = products_df.sample().iloc[0]
    client = clients_df.sample().iloc[0]
    user = users_df.sample().iloc[0]
    
    quantity = random.randint(1, 10)
    total_price = round(product['price'] * quantity, 5) # Round to 5 decimal places
    sale_date = fake.date_between(start_date='-1y', end_date='today')
    
    sales_data.append({
        'sale_id': fake.uuid4(),
        'product_id': product['id'],
        'product_name': product['name'],
        'client_id': client['id'],
        'client_name': client['fullname'],
        'user_id': user['id'],
        'user_name': user['username'],
        'quantity': quantity,
        'total_price': total_price,
        'sale_date': sale_date
    })

# Create a DataFrame and save to CSV
df = pd.DataFrame(sales_data)
df.to_csv(f'./salesdata_{num_records}.csv', index=False)
print ('Sales data generation completed and saved to salesdata.csv')
print (df.head())
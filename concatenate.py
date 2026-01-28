import pandas as pd
import numpy as np

customer_cols = [
    "id",
    "first_name",
    "last_name",
    "gender",
    "DOB",
    "LoyaltyMember",
    "EmailList",
    "Source"	
]

order_cols = [
    "CustomerID",
    "LocationID",
    "Date",
    "Time",
    "EmployeeID",
    "OrderID",
]

# orig customers data
customers_orig = pd.read_excel('./data_original/Customers.xlsx')

# join with existing data
new_customers_df = pd.read_excel('./data_new/newCustomers.xlsx')
new_customers_df.rename(columns={'CustomerID': 'id'}, inplace=True)
new_customers_df = new_customers_df[['id', 'first_name', 'last_name', 'gender', 'DOB', 'LoyaltyMember', 'EmailList', 'Source']]


customers_final_df = (
    pd.concat([customers_orig, new_customers_df], ignore_index=True)
      .drop_duplicates(subset=["id"], keep="first")  # or keep="last"
)
customers_final_df[customer_cols].drop_duplicates().rename(columns={
    "CustomerID": "id"
}).to_excel('./data_new/FULL_Customers.xlsx', sheet_name='Customers', index=False)

# orig customers data
orders_orig = pd.read_excel('./data_original/OrderInfo.xlsx')

# join with existing data
new_orders_df = pd.read_excel('./data_new/newOrderInfo.xlsx')
# new_orders_df.rename(columns={'CustomerID': 'id'}, inplace=True)
new_orders_df = new_orders_df[order_cols]


orders_final_df = (
    pd.concat([orders_orig, new_orders_df], ignore_index=True)
      .drop_duplicates(subset=["OrderID"], keep="first")  # or keep="last"
)

orders_final_df[order_cols].drop_duplicates(subset=["CustomerID", "OrderID"]) \
    .to_excel('./data_new/FULL_OrderInfo.xlsx', sheet_name='OrderInfo', index=False)
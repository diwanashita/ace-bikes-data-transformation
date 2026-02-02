import numpy as np
import pandas as pd
import pickle


lineitemsorig_df = pd.read_csv('./data_original/LineItemSales.csv')
# lineitemsorig_df

orders_df = pd.read_excel('./data_original/OrderInfo.xlsx')

order_small = orders_df[['OrderID', 'Date', 'LocationID']].copy()

lineitems_with_date_df = lineitemsorig_df.merge(
    order_small,
    on='OrderID',
    how='left',
    validate='many_to_one' # many line items per order; one matching order row
)

lineitems_with_date_df.isna().sum() # confirm no missing values

lineitemsnew_df = pd.read_csv('data_new/newLineItemSales.csv')
lineitem_full_df = pd.concat([lineitems_with_date_df, lineitemsnew_df], ignore_index=True)

# Parse to datetime, then format as date-only string
lineitem_full_df["Date"] = (
    pd.to_datetime(lineitem_full_df["Date"], errors="coerce")
      .dt.strftime("%Y-%m-%d")
)

lineitem_full_df.to_csv('./data_full/LineItemSales.csv', index=False)

# Location establishment years
# LOAD

# new_stores = {
#     2022: {'location': 'L12', 'employees_needed': 5},
#     2023: {'location': 'L13', 'employees_needed': 5},
#     2024: {'location': 'L14', 'employees_needed': 5},
#     2025: {'location': 'L15', 'employees_needed': 6}
# }
with open("locations.pkl", "rb") as f:
    loaded_dict = pickle.load(f)


location_years = {
    'L01': 2017, 'L02': 2018, 'L03': 2018, 'L04': 2019, 'L05': 2019,
    'L06': 2020, 'L07': 2020, 'L08': 2020, 'L09': 2021, 'L10': 2021,
    'L11': 2021
}

for key in loaded_dict.keys():
    loc = loaded_dict[key]['location']
    location_years[loc] = key

print(location_years)

print("Generating Inventory | This step will take a few minutes :)")

def generate_inventory_dataframe(line_items_df, y1=2017, y2=2025, num_items=64):
    """
    Generate inventory dataframe with realistic movements
    
    Parameters:
    - line_items_df: DataFrame with columns [LineItemID, OrderID, ItemID, Qty, Date, LocationID]
    - y1: Start year
    - y2: End year
    - num_items: Total number of items (1 to num_items)
    """
    
    # Convert Date column to datetime
    line_items_df['Date'] = pd.to_datetime(line_items_df['Date'])
    line_items_df['Month'] = line_items_df['Date'].dt.to_period('M').dt.to_timestamp()
    
    # Calculate sales by month, location, and item
    sales_summary = line_items_df.groupby(['Month', 'LocationID', 'ItemID'])['Qty'].sum().reset_index()
    sales_summary.columns = ['Month', 'LocationID', 'ItemID', 'SoldQty']
    
    # Generate date range
    date_range = pd.date_range(start=f'{y1}-01-01', end=f'{y2}-12-01', freq='MS')
    
    # Create all combinations of dates, locations, and items
    # But only include locations that were open in that month
    records = []
    
    for date in date_range:
        year = date.year
        month = date.month
        
        # Determine which locations are open
        open_locations = [loc for loc, est_year in location_years.items() 
                         if est_year <= year or (est_year == year and month >= 1)]
        
        for location in open_locations:
            for item_id in range(1, num_items + 1):
                records.append({
                    'Month': date,
                    'LocationID': location,
                    'ItemID': item_id
                })
    
    # Create base dataframe
    inventory_df = pd.DataFrame(records)
    
    # Merge with sales data
    inventory_df = inventory_df.merge(sales_summary, 
                                      on=['Month', 'LocationID', 'ItemID'], 
                                      how='left')
    inventory_df['SoldQty'] = inventory_df['SoldQty'].fillna(0).astype(int)
    
    # Sort by location, item, and month
    inventory_df = inventory_df.sort_values(['LocationID', 'ItemID', 'Month']).reset_index(drop=True)
    
    # Set inventory parameters
    # Different items might have different thresholds; here we'll use item-based variation
    np.random.seed(1234)
    item_thresholds = {item_id: np.random.randint(30, 100) for item_id in range(1, num_items + 1)}
    
    # Initialize columns
    inventory_df['BeginningOnHand'] = 0
    inventory_df['PurchasedQty'] = 0
    inventory_df['AdjustmentsQty'] = 0
    
    # Calculate inventory movements month by month
    for idx, row in inventory_df.iterrows():
        location = row['LocationID']
        item_id = row['ItemID']
        month = row['Month']
        sold_qty = row['SoldQty']
        
        threshold = item_thresholds[item_id]
        
        # Check if this is the first month for this location-item combination
        prev_rows = inventory_df[
            (inventory_df['LocationID'] == location) & 
            (inventory_df['ItemID'] == item_id) & 
            (inventory_df['Month'] < month)
        ]
        
        if len(prev_rows) == 0:
            # First month: start with initial stock
            beginning_on_hand = threshold # will need to hardcode to include 2022
            inventory_df.at[idx, 'BeginningOnHand'] = beginning_on_hand
        else:
            # Get ending inventory from previous month
            prev_idx = prev_rows.index[-1]
            prev_row = inventory_df.loc[prev_idx]
            beginning_on_hand = (prev_row['BeginningOnHand'] + 
                               prev_row['PurchasedQty'] - 
                               prev_row['SoldQty'] + 
                               prev_row['AdjustmentsQty'])
            inventory_df.at[idx, 'BeginningOnHand'] = max(0, beginning_on_hand)
        
        # Calculate purchases: top up if below 20% of threshold
        current_stock = inventory_df.at[idx, 'BeginningOnHand']
        
        if current_stock < threshold * 0.2:
            # Purchase enough to reach threshold
            purchase_qty = threshold - current_stock
            inventory_df.at[idx, 'PurchasedQty'] = purchase_qty
        else:
            inventory_df.at[idx, 'PurchasedQty'] = 0
        
        # Add random adjustments (shrink, damage, corrections)
        # Small probability of adjustments, can be positive or negative
        if np.random.random() < 0.15:  # 15% chance of adjustment
            # Adjustments typically small, mostly negative (shrink/damage)
            adjustment = np.random.choice(
                [-5, -4, -3, -2, -1, 0, 1, 2], 
                p=[0.1, 0.15, 0.2, 0.25, 0.15, 0.05, 0.05, 0.05]
            )
            inventory_df.at[idx, 'AdjustmentsQty'] = adjustment
        else:
            inventory_df.at[idx, 'AdjustmentsQty'] = 0
    
    # Convert Month to string format YYYY-MM-01
    inventory_df['Month'] = inventory_df['Month'].dt.strftime('%Y-%m-%d')
    
    # Ensure proper column order and data types
    inventory_df = inventory_df[['Month', 'LocationID', 'ItemID', 'BeginningOnHand', 
                                 'PurchasedQty', 'SoldQty', 'AdjustmentsQty']]
    
    inventory_df['ItemID'] = inventory_df['ItemID'].astype(int)
    inventory_df['BeginningOnHand'] = inventory_df['BeginningOnHand'].astype(int)
    inventory_df['PurchasedQty'] = inventory_df['PurchasedQty'].astype(int)
    inventory_df['SoldQty'] = inventory_df['SoldQty'].astype(int)
    inventory_df['AdjustmentsQty'] = inventory_df['AdjustmentsQty'].astype(int)
    
    return inventory_df


# Example usage with sample data
if __name__ == "__main__":
    # Load sample line items
    line_items_df = lineitem_full_df.copy()
    
    # Generate inventory dataframe
    inventory_df = generate_inventory_dataframe(line_items_df, y1=2017, y2=2025, num_items=64)
    
    # Display sample
    print("Inventory DataFrame Sample:")
    print(inventory_df.head(20))
    print(f"\nTotal rows: {len(inventory_df)}")
    print(f"\nDataFrame info:")
    print(inventory_df.info())
    
    # Show some statistics
    print("\n\nSummary by Location:")
    print(inventory_df.groupby('LocationID').agg({
        'SoldQty': 'sum',
        'PurchasedQty': 'sum',
        'AdjustmentsQty': 'sum'
    }))
    
    
inventory_df.to_csv('./data_full/Inventory.csv', index=False)


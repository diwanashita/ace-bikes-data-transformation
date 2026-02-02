import pandas as pd
import numpy as np

# fix date string for concate

np.random.seed(1234)


lineitem_df = pd.read_csv('data_original/LineItemSales.csv')
orders_df = pd.read_excel('data_new/newOrderInfo.xlsx')


# Initialize list to store line items
line_item_id = int(lineitem_df["LineItemID"].max())


line_items = []
for _, order in orders_df.iterrows():
    order_id = order['OrderID']
    date = order['Date']
    location = order['LocationID']
    
    # Generate 1-3 line items per order
    num_line_items = np.random.randint(1, 5)
    
    # Track items already added to this order to avoid duplicates
    items_in_order = set()
    
    for _ in range(num_line_items):
        # Generate ItemID with weighted probability
        # Items 1-53 are common, 54-61 are much less common
        if np.random.random() < 0.90:  # 90% chance for items 1-53
            item_id = np.random.randint(1, 54)
        else:  # 10% chance for items 54-61
            item_id = np.random.randint(54, 62)
        
        # Avoid duplicate items in the same order
        while item_id in items_in_order:
            if np.random.random() < 0.90:
                item_id = np.random.randint(1, 54)
            else:
                item_id = np.random.randint(54, 62)
        
        items_in_order.add(item_id)
        
        # Generate Quantity based on ItemID
        if 1 <= item_id <= 21:
            quantity = 1  # Strictly 1 for items 1-21
        else:
            if np.random.random() < 0.98:
                quantity = 1
            else:    
                quantity = np.random.randint(2, 5)  # 1-4 for other items
        
        # Generate DiscountID with specified probabilities
        discount_rand = np.random.random()
        if discount_rand < 0.02:  # 2% chance
            discount_id = 'D1'
        elif discount_rand < 0.04:  # 2% chance
            discount_id = 'D2'
        elif discount_rand < 0.05:  # 1% chance
            discount_id = 'D3'
        else:  # 95% chance
            discount_id = None
        
        # Create line item
        line_items.append({
            'LineItemID': line_item_id,
            'OrderID': order_id,
            'ItemID': item_id,
            'Qty': quantity,
            'DiscountID': discount_id,
            'Date': date,
            'LocationID': location
        })

        
        line_item_id += 1

# Create DataFrame
line_items_df = pd.DataFrame(line_items)

# Display results
print(f"Generated {len(line_items_df)} line items for {len(orders_df)} orders")
print("\nFirst 20 line items:")
print(line_items_df.head(20))

# Save to CSV
# line_items_df.to_csv('line_items.csv', index=False)
print("\nLine items saved to 'line_items.csv'")

# Show summary statistics
print("\nSummary Statistics:")
print(f"Total line items: {len(line_items_df)}")
print(f"Average line items per order: {len(line_items_df)/len(orders_df):.2f}")
print(f"\nItemID distribution:")
print(f"  Items 1-53: {len(line_items_df[line_items_df['ItemID'] <= 53])}")
print(f"  Items 54-61: {len(line_items_df[line_items_df['ItemID'] >= 54])}")
print(f"\nDiscount distribution:")
print(line_items_df['DiscountID'].value_counts(dropna=False))

line_items_df.drop_duplicates(subset=["LineItemID", "OrderID"]) \
    .to_csv('./data_new/newLineItemSales.csv', index=False)






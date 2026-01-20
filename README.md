# Ace Bikes Data Transformation
---

## Data Extension Plan

Table/file dependency: 
``` bash
Customers
    ↓
Employees
    ↓
Inventory
    ↓
OrderInfo
    ↓
LineItemSales
    ↓
InventoryCounts
    ↓
Reviews (2023, 2024, 2025)
    ↓
WebStats (2023, 2024, 2025)
```

1. **Customers.xlsx:** add new customers monthly from 2023-2025 + acquired from new stores
    - New customer growth rate ~5-8% year-over-year (YoY)
    - `DOB`/Age between 18-70, sampled randomly
    - `LoyaltyMember` rate ~30-40% @ True (following current trend)
    - `EmailList` to be correlated with `LoyaltyMember`
    - `Source` to keep existing distribution (e.g., Web, In-store, Referral)
    - No deletions, no ID reuse

2. **Employees.xlsx:** add 1-3 new hires per year + employees for new stores; no mass layoffs
    - New `EmployeeNumber` when hired
    - 1 = emplyed; 0 or blank = not employed
    - Once terminated, all future months = 0
    - Employee count slow-growing, not volatile

3. **Inventory.xlsx:** add new counts and purchases per year (include new stores)
    - New `IDs` for new counts & purchases
    - New locations add inventory from their opening year (assuming Jan 1 for new openings)
    - Inventory structure should not change

4. **OrderInfo.xlsx:** use 2017-2022 order volume patters to extend daily orders for 2023-2025
    - New order growth rate @ ~5-6%
    - Each order must have existing `CustomerID`
    - `EmployeeID` must be active on order date
    - Date distribution: summer + holiday spikes
    - Time distribution: business hours
    - Consistent location mix but spike in first month of new location openings
    - Note: this drives almost everything else

5. **LineItmeSales.csv:** add new line items per order for 2023-2025
    - 1-4 line items per order
    - `Qty` usually = 1
    - Item popularity to follow historical proportions
    - `DiscountID` to be used on ~20-30% of the orders; `DiscountID` must exist in discount lookup
    - Every `OrderID` must appear at least once here

6. **InventoryCounts.xlsx:** should respond to sales
    - Monthly snapshots each year
    - Unsure

7. **Reviews files:** create new files for 2023, 2024 & 2025
    - Reviews are a subset of orders
    - Review rate @ 10-15% of orders
    - Review `Date` @ 3-21 days after purchase
    - `Rating` distribution @ mostly 5-4 starts, very few 1 stars
    - `Platform` @ same distribution as previous years
    - One review per order max

8. **WebStats files:** create new files for 2023, 2024 & 2025
    - WebStats should correlate with online orders
    - Sessions grow faster than sales (~ +10% YoY)
    - `Conversion_rate` = mostly stable, slight improvement over time
    - `Device_type` = increasing mobile share
    - `Bounce_rate` inversely related to `time_on_page` 
    - Don't need 1:1 user, just order mapping for macro alignment

### Validation checks

Check after generation:
- [ ] All foreign keys resolve
- [ ] No negative inventory
- [ ] No orders without line items
- [ ] No reviews before purchase
- [ ] Employee active on order date
- [ ] 2023-2025 "looks like" evolved 2017-2022

### Implementaiton Tech Stack

Python: 
- pandas
- numpy
- faker
- Fixed random seed (1234) 
- One script per stage:
``` bash01_customers.py
02_employees.py
03_orders.py
04_line_items.py
05_inventory_counts.py
06_reviews.py
07_webstats.py
```

Outputs:
- Same file formats
- Same column names
- New files for 2023-2025 only; not overwriting originals

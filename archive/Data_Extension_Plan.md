# Ace Bikes Data Transformation Plan
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

1. **Customers.xlsx:** add new customers yearly from 2023-2025 + acquired from new stores
    - New customer growth rate ~5-8% year-over-year (YoY)
    - `DOB` between 18-70, sampled randomly
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
    - Review rate: 2022=2919 reviews, 2021=2878, 2022=2088, 2019=1298, 2018=776, 2017=209
    - `Rating` distribution on a scale of 1-10, but only 6-10 ratings, more leaning on higher end
    - `Platform` distribution between Facebook, Yelp and Google, with preference in that order so Facebooks has slightly more dist then Telp then Google (ex. 35%-34%-31% respectively)

8. **WebStats files:** create new files for 2023, 2024 & 2025
    - Sessions grow faster than sales (2017=500 stats, 2018=900, 2019=1500, 2020=2000, 2021=3000, 2022=4000)
    - `Conversion_rate` = mostly stable, slight improvement over time but has lots of variance within a year
    - `Device_type` = increasing mobile share but still distributed
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

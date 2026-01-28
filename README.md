# Ace Bikes Data Generator

Generates synthetic Ace Bikes data for extended years based on existing historical files.

⸻

Usage

1. Run install: 
``` bash
make intall
```

2. Generate new data:
``` bash
make generate
```

⸻

What the Script Does
- Extends existing Ace Bikes data forward in time
- Does not overwrite original files
- Uses a fixed random seed for reproducibility

Generated Data
- Customers
- New customers added each year
- DOB between 18–71
- Loyalty and email flags with correlation
- Assigned to existing or newly opened locations
- Orders
- One order per new customer
- Small number of repeat orders in later years
- Dates spread across the year
- Business-hour timestamps
- Locations
- Existing locations inferred from historical data
- One new location opened per generated year
- Employees
- New employees hired as needed
- Employees assigned only if active on order date
- Low termination probability

⸻

Input Files (required in ./data_original/)
- Customers.xlsx
- OrderInfo.xlsx
- Employees.xlsx
- Ace_Bikes_Data.xlsx

⸻

Output Files (written to ./data_new/)
- newCustomers.xlsx
- newOrderInfo.xlsx
- newEmployees.xlsx

Original files are never modified.

⸻

Tech Stack
- Python
- pandas
- numpy
- faker

⸻

Random seed used: 1234

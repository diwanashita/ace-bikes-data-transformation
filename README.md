# Ace Bikes Data Generator

Generates synthetic Ace Bikes data for extended years based on existing historical files.


## Usage

1. Run install: 
``` bash
make install
```

2. Generate new data:

This project is fully automated. You can extend the existing dataset forward by specifying: 
- `START_YEAR` : the first year to generate (inclusive)
- `NUM` : how many years to generate


**DEFAULT USE**

If you run without parameters, the Makefile defaults will be used (START_YEAR=2022 NUM=4): 
``` bash
make generate
```


Example Use: 

Generate the next 10 years starting from 2022 (creates 2022-2031):
``` bash
make generate START_YEAR=2022 NUM=10
```

3. Update `Ace_Bikes_Data.xlsx` to include the tables

Table Glossary: 

| **Table Columns** | **Table Name** |
|---|---|
| A:D | EmployeeDates |
| F:L | EmployeeReviewInfo |
| N:O | Reason |
| Q:V | Items |
| X:AA | Categories |
| AC:AE | Vendors |
| AG:AM | VendorScore |
| AO:AP | Returns |
| AR:AS | ReturnReason |
| AU:AW | Discounts |
| AY:BC | Locations |
| BE:BF | OnlineOrderShipTo |
| BH:BK | Expenses |
| BM:BN | ExpenseType |
| BP:BQ | LeaseCosts |
| BS:BU | Research |
| BW:BY | ExcursionTypes |




## Info About This Project

### What the Script Does: 
- Extends existing Ace Bikes data forward in time
- Does not overwrite original files
- Uses a fixed random seed for reproducibility

### Generated Data: 
- Customers.xlsx
- Employees.xlsx
- OrderInfo.xlsx
- LineItemSales.csv
- Inventory.csv
- Review folder/files
- WebStat folder/files


### Input Files (required in ./data_original/)
- Customers.xlsx
- OrderInfo.xlsx
- Employees.xlsx
- Ace_Bikes_Data.xlsx
- LineItemSales.csv
- Reviews folder
- Webstats folder
- Ace_Bikes_Data.xlsx
- Data_Dictionary.xlsx
- New_Categories.xlsx


### Output Files written to ./data_full/ (with historic data attached): 
- Customers.xlsx
- Employees.xlsx
- OrderInfo.xlsx
- LineItemSales.csv
- Inventory.csv
- Reviews: 
    - One file per year from historic start year (2017) till end year
- WebStat:
    - One file per year from historic start year (2017) till end year
- Ace_Bikes_Data.xlsx (copied over from .data_original/)
- Data_Dictionary.xlsx (copied over from .data_original/)
- New_Categories.xlsx (copied over from .data_original/)


### Output Files written to ./data_new/ (without historic data attached):
- newCustomers.xlsx
- newOrderInfo.xlsx
- newEmployees.xlsx
- newLineItemSales.xlsx
- Reviews: 
    - One file per year from START_YEAR till end year
- Webstats:
    - One file per year from START_YEAR till end year



**Original files are never modified**


## Tech Stack
Python
- pandas
- numpy
- faker

*Random seed used: 1234*

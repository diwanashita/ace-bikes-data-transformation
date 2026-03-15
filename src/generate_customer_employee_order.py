"""
Ace Bikes Data Generator - Extended Years (PER-LOCATION FIX)
=============================================================
Generates synthetic customer and employee data for specified years.
New customers and repeat orders are generated PER LOCATION to guarantee
year-over-year growth at every store.

Usage:
    python script.py <baseline_year> <num_years>
    
Example:
    python script.py 2022 4
    This generates data for 2022, 2023, 2024, 2025
"""

import sys
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta, date
import warnings
import pickle
warnings.filterwarnings('ignore')


# ============================================================================
# COMMAND LINE ARGUMENTS
# ============================================================================

def parse_arguments():
    """Parse and validate command line arguments"""
    if len(sys.argv) != 3:
        print("ERROR: Missing arguments!")
        print("Usage: python script.py <baseline_year> <num_years>")
        print("Example: python script.py 2022 4")
        sys.exit(1)
    
    try:
        baseline_year = int(sys.argv[1])
        num_years = int(sys.argv[2])
        
        if baseline_year < 2000 or baseline_year > 2030:
            raise ValueError("Baseline year must be between 2000 and 2030")
        if num_years < 1 or num_years > 10:
            raise ValueError("Number of years must be between 1 and 10")
        
        return baseline_year, num_years
    
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)


# Get command line arguments
BASELINE_YEAR, NUM_YEARS = parse_arguments()
YEARS_TO_GENERATE = list(range(BASELINE_YEAR, BASELINE_YEAR + NUM_YEARS))

print("=" * 80)
print("ACE BIKES DATA GENERATOR (PER-LOCATION FIX)")
print("=" * 80)
print(f"Baseline Year: {BASELINE_YEAR}")
print(f"Number of Years: {NUM_YEARS}")
print(f"Years to Generate: {YEARS_TO_GENERATE}")
print("=" * 80)


# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

# Set random seed for reproducibility
RANDOM_SEED = 1234
np.random.seed(RANDOM_SEED)
fake = Faker()
Faker.seed(RANDOM_SEED)

# Customer source distribution
SOURCE_OPTIONS = ['Newspaper', 'Social', 'Referral', 'WalkIn', 'Online', 'Advertisement']
SOURCE_WEIGHTS = [0.10, 0.25, 0.15, 0.30, 0.15, 0.05]

# Gender distribution
GENDER_OPTIONS = ['M', 'F', 'X']
GENDER_WEIGHTS = [0.48, 0.50, 0.02]

# Growth rates — applied PER LOCATION
NEW_CUSTOMER_GROWTH_RATE = 0.15   # 15% more unique customers per location per year
ORDER_GROWTH_RATE = 0.10          # 10% more total orders per location per year
NEW_STORE_FIRST_YEAR_CUSTOMERS = 400  # target unique customers for a brand-new store

# Employee settings
EMPLOYEE_GENDER_OPTIONS = ['Male', 'Female', 'Other']
EMPLOYEE_GENDER_WEIGHTS = [0.44, 0.45, 0.11]
TRAINING_PROB = 0.15

# New store configuration
NEW_STORE_EMPLOYEES = 5


# ============================================================================
# DATA LOADING
# ============================================================================

print("\n[STEP 1] Loading existing data files...")

try:
    customers_orig = pd.read_excel('./data_original/Customers.xlsx')
    orderinfo_orig = pd.read_excel('./data_original/OrderInfo.xlsx')
    
    customers_orig['DOB'] = customers_orig['DOB'].dt.date
    orderinfo_orig['Date'] = orderinfo_orig['Date'].dt.date
    
    print(f"✓ Loaded {len(customers_orig)} customers")
    print(f"✓ Loaded {len(orderinfo_orig)} orders")
    
    employees_prof_orig = pd.read_excel('./data_original/Employees.xlsx')
    employees_dates_orig = pd.read_excel('./data_original/Ace_Bikes_Data.xlsx', 
                                         usecols=['EmployeeID', 'StartDate', 'TerminationDate', 'LocationID'])
    
    employees_prof_orig['DOB'] = employees_prof_orig['DOB'].dt.date
    employees_dates_orig['StartDate'] = employees_dates_orig['StartDate'].dt.date
    employees_dates_orig['TerminationDate'] = employees_dates_orig['TerminationDate'].dt.date
    
    employees_orig = employees_prof_orig.merge(
        employees_dates_orig,
        left_on='Employee Number',
        right_on='EmployeeID',
        how='left'
    )
    employees_orig = employees_orig.drop(columns=['EmployeeID']).rename(columns={'Employee Number': 'EmployeeID'})
    
    print(f"✓ Loaded {len(employees_orig)} employees")
    
except FileNotFoundError as e:
    print(f"✗ ERROR: Could not find data file: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ ERROR loading data: {e}")
    sys.exit(1)


# ============================================================================
# INFER EXISTING LOCATIONS AND NEW STORES FROM DATA
# ============================================================================

print("\n[STEP 2] Inferring locations from existing data...")

EXISTING_LOCATIONS = sorted(orderinfo_orig['LocationID'].dropna().unique().tolist())
print(f"✓ Found {len(EXISTING_LOCATIONS)} existing locations: {EXISTING_LOCATIONS}")

def generate_next_location_id(existing_locations):
    location_numbers = []
    for loc in existing_locations:
        num_str = loc.replace('L', '').replace('l', '')
        try:
            location_numbers.append(int(num_str))
        except ValueError:
            continue
    if location_numbers:
        next_num = max(location_numbers) + 1
        if next_num < 10:
            return f"L0{next_num}"
        else:
            return f"L{next_num}"
    else:
        return "L01"

NEW_STORES = {}
current_locations = EXISTING_LOCATIONS.copy()

for year in YEARS_TO_GENERATE:
    if year >= BASELINE_YEAR:
        new_location = generate_next_location_id(current_locations)
        employees_needed = NEW_STORE_EMPLOYEES + 1 if year == YEARS_TO_GENERATE[-1] else NEW_STORE_EMPLOYEES
        NEW_STORES[year] = {
            'location': new_location,
            'employees_needed': employees_needed
        }
        current_locations.append(new_location)

with open("locations.pkl", "wb") as f:
    pickle.dump(NEW_STORES, f)

print(f"✓ Planned new stores:")
for year, store_info in NEW_STORES.items():
    print(f"  - {year}: {store_info['location']} ({store_info['employees_needed']} employees)")


# ============================================================================
# DATA PREPARATION
# ============================================================================

print("\n[STEP 3] Preparing base data...")

# Merge customers with orders
customer_order_df = customers_orig.merge(
    orderinfo_orig,
    left_on='id',
    right_on='CustomerID',
    how='left'
)
customer_order_df = customer_order_df.drop(columns={'CustomerID'}).rename(columns={'id': 'CustomerID'})

# Initialize ID trackers
next_order_id = int(customer_order_df['OrderID'].max() + 1)
next_customer_id = int(customer_order_df['CustomerID'].max() + 1)
next_employee_id = int(employees_orig['EmployeeID'].max() + 1)

# ---- PER-LOCATION BASELINES from the most recent year in original data ----
customer_order_df['_Date'] = pd.to_datetime(customer_order_df['Date'], errors='coerce')
most_recent_year = customer_order_df['_Date'].dt.year.max()
recent_year_data = customer_order_df[customer_order_df['_Date'].dt.year == most_recent_year]

# Per-location: unique customers and total orders in the most recent year
loc_unique_customers = recent_year_data.groupby('LocationID')['CustomerID'].nunique().to_dict()
loc_total_orders = recent_year_data.groupby('LocationID').size().to_dict()

print(f"\nPer-location baselines (from {most_recent_year}):")
for loc in sorted(loc_unique_customers.keys()):
    print(f"  {loc}: {loc_unique_customers[loc]} unique customers, {loc_total_orders[loc]} orders")

print(f"\n✓ Next Customer ID: {next_customer_id}")
print(f"✓ Next Order ID: {next_order_id}")
print(f"✓ Next Employee ID: {next_employee_id}")


# ============================================================================
# HELPER: Generate a single customer record
# ============================================================================

def make_customer_record(location, year, next_customer_id, next_order_id, is_new_store=False):
    """Generate a single new customer dict for a given location and year."""
    
    # Random date within the year
    day_of_year = np.random.randint(1, 366)
    customer_date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    
    # Business hours
    hour = np.random.randint(9, 18)
    minute = np.random.randint(0, 60)
    second = np.random.randint(0, 60)
    customer_time = f"{hour:02d}:{minute:02d}:{second:02d}"
    
    # Demographics
    dob = fake.date_of_birth(minimum_age=18, maximum_age=71)
    gender = np.random.choice(GENDER_OPTIONS, p=GENDER_WEIGHTS)
    
    if gender == 'M':
        first_name = fake.first_name_male()
    elif gender == 'F':
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name_nonbinary()
    last_name = fake.last_name()
    
    # Loyalty & email
    if is_new_store:
        loyalty_member = np.random.choice([0.0, 1.0], p=[0.50, 0.50])
    else:
        loyalty_member = np.random.choice([0.0, 1.0], p=[0.65, 0.35])
    
    if loyalty_member == 1.0:
        email_list = np.random.choice([0.0, 1.0], p=[0.20 if is_new_store else 0.30, 
                                                       0.80 if is_new_store else 0.70])
    else:
        email_list = np.random.choice([0.0, 1.0], p=[0.60 if is_new_store else 0.70, 
                                                       0.40 if is_new_store else 0.30])
    
    # Source
    if is_new_store:
        source = np.random.choice(SOURCE_OPTIONS, p=[0.05, 0.20, 0.10, 0.35, 0.10, 0.20])
    else:
        source = np.random.choice(SOURCE_OPTIONS, p=SOURCE_WEIGHTS)
    
    return {
        'CustomerID': next_customer_id,
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'DOB': dob.strftime('%Y-%m-%d'),
        'LoyaltyMember': loyalty_member,
        'EmailList': email_list,
        'Source': source,
        'LocationID': location,
        'Date': customer_date.strftime('%Y-%m-%d'),
        'Time': customer_time,
        'EmployeeID': None,
        'OrderID': next_order_id
    }


def make_repeat_order(sampled_customer, year, next_order_id):
    """Generate a repeat order dict from an existing customer."""
    
    day_of_year = np.random.randint(1, 366)
    order_date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    
    hour = np.random.randint(9, 21)
    minute = np.random.randint(0, 60)
    second = np.random.randint(0, 60)
    order_time = f"{hour:02d}:{minute:02d}:{second:02d}"
    
    return {
        'CustomerID': sampled_customer['CustomerID'],
        'first_name': sampled_customer['first_name'],
        'last_name': sampled_customer['last_name'],
        'gender': sampled_customer['gender'],
        'DOB': sampled_customer['DOB'],
        'LoyaltyMember': sampled_customer['LoyaltyMember'],
        'EmailList': sampled_customer['EmailList'],
        'Source': sampled_customer['Source'],
        'LocationID': sampled_customer['LocationID'],
        'Date': order_date.strftime('%Y-%m-%d'),
        'Time': order_time,
        'EmployeeID': None,
        'OrderID': next_order_id
    }


# ============================================================================
# EMPLOYEE MANAGEMENT FUNCTIONS
# ============================================================================

def create_new_employee(location, year, new_employees_df):
    global next_employee_id
    
    gender = np.random.choice(EMPLOYEE_GENDER_OPTIONS, p=EMPLOYEE_GENDER_WEIGHTS)
    if gender == 'Male':
        first_name = fake.first_name_male()
    elif gender == 'Female':
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name()
    last_name = fake.last_name()
    
    dob = fake.date_of_birth(minimum_age=20, maximum_age=50)
    start_date = pd.Timestamp(f"{year}-01-{np.random.randint(1, 5):02d}")
    
    new_employee = {
        'EmployeeID': next_employee_id,
        'FName': first_name,
        'LName': last_name,
        'gender': gender,
        'SkillsTraining': np.random.choice([True, False]),
        'SalesmanshipTraining': np.random.choice([True, False]),
        'ProductTraining': np.random.choice([True, False]),
        'DOB': dob,
        'StartDate': start_date,
        'TerminationDate': pd.NaT,
        'LocationID': location
    }
    
    new_employee_df = pd.DataFrame([new_employee])
    new_employees_df = pd.concat([new_employees_df, new_employee_df], ignore_index=True)
    
    employee_id = next_employee_id
    next_employee_id += 1
    
    return employee_id, new_employees_df


def prestaff_new_store(location, year, num_employees, new_employees_df):
    global next_employee_id
    print(f"    - Pre-staffing {location} with {num_employees} employees")
    for _ in range(num_employees):
        _, new_employees_df = create_new_employee(location, year, new_employees_df)
    return new_employees_df


def assign_employee(row, new_employees_df):
    if pd.notna(row["EmployeeID"]):
        return row['EmployeeID'], new_employees_df
    
    order_date = pd.Timestamp(row['Date'])
    order_year = order_date.year
    location = row['LocationID']
    
    if isinstance(location, dict):
        location = location.get('location', None)
    if location is None or pd.isna(location):
        return None, new_employees_df
    
    eligible = new_employees_df[new_employees_df['LocationID'] == location]
    eligible = eligible[eligible['StartDate'] <= order_date]
    eligible = eligible[
        (eligible['TerminationDate'].isna()) | 
        (eligible['TerminationDate'] > order_date)
    ]
    
    if len(eligible) > 0:
        return np.random.choice(eligible['EmployeeID'].values), new_employees_df
    else:
        employee_id, new_employees_df = create_new_employee(location, order_year, new_employees_df)
        return employee_id, new_employees_df


# ============================================================================
# MAIN GENERATION LOGIC — PER LOCATION
# ============================================================================

print("\n[STEP 4] Generating new customers and repeat orders PER LOCATION...")

all_new_records = []

# Build a running pool of all customers (original + newly generated) for repeat sampling
# We'll append to this as we go through each year
pool_df = customer_order_df.copy()
pool_df['_Date'] = pd.to_datetime(pool_df['Date'], errors='coerce')

# Track per-location baselines (these update year over year)
running_loc_unique = dict(loc_unique_customers)   # unique customers last year
running_loc_orders = dict(loc_total_orders)        # total orders last year

for year in YEARS_TO_GENERATE:
    print(f"\n  ========== Year {year} ==========")
    year_records = []
    
    # Determine which locations are active this year
    active_locations = EXISTING_LOCATIONS.copy()
    new_store_this_year = NEW_STORES.get(year)
    
    # Add stores from prior generated years
    for y in range(YEARS_TO_GENERATE[0], year):
        if y in NEW_STORES:
            active_locations.append(NEW_STORES[y]['location'])
    
    # ------------------------------------------------------------------
    # A) EXISTING LOCATIONS — generate per-location new customers + repeats
    # ------------------------------------------------------------------
    for loc in active_locations:
        prior_unique = running_loc_unique.get(loc, 0)
        prior_orders = running_loc_orders.get(loc, 0)
        
        # Jittered growth rates — uniform draw within a band
        loc_cust_rate = np.random.uniform(0.7, 0.13)   # 12-17% new customers
        loc_order_rate = np.random.uniform(0.04, 0.10)   # 7-13% order growth
        
        # Target counts for this year at this location
        target_new_customers = max(1, int(prior_unique * loc_cust_rate))
        target_total_orders = max(1, int(prior_orders * (1 + loc_order_rate)))
        target_repeat_orders = max(0, target_total_orders - target_new_customers)
        
        # --- New customers for this location ---
        for _ in range(target_new_customers):
            rec = make_customer_record(loc, year, next_customer_id, next_order_id)
            year_records.append(rec)
            next_customer_id += 1
            next_order_id += 1
        
        # --- Repeat orders for this location ---
        # Sample from existing customers at this location
        loc_pool = pool_df[
            (pool_df['LocationID'] == loc) &
            (pool_df['_Date'].dt.year <= year)
        ]
        
        if len(loc_pool) > 0 and target_repeat_orders > 0:
            sampled_rows = loc_pool.sample(n=target_repeat_orders, replace=True)
            for _, sampled_customer in sampled_rows.iterrows():
                rec = make_repeat_order(sampled_customer, year, next_order_id)
                year_records.append(rec)
                next_order_id += 1
        
        # Update running baselines for next year
        running_loc_unique[loc] = prior_unique + target_new_customers
        running_loc_orders[loc] = target_total_orders
        
        print(f"    {loc}: {target_new_customers} new + {target_repeat_orders} repeat = {target_new_customers + target_repeat_orders} orders  (prior unique: {prior_unique}, new unique total: {running_loc_unique[loc]})")
    
    # ------------------------------------------------------------------
    # B) NEW STORE THIS YEAR — seed with ~400 customers
    # ------------------------------------------------------------------
    if new_store_this_year:
        new_loc = new_store_this_year['location']
        active_locations.append(new_loc)
        
        # New store gets ~NEW_STORE_FIRST_YEAR_CUSTOMERS unique new customers
        # with some jitter, and a jittered repeat rate within the first year
        new_store_new = int(np.random.normal(NEW_STORE_FIRST_YEAR_CUSTOMERS, 40))
        new_store_new = max(300, new_store_new)  # floor at 300
        repeat_rate = max(0.10, np.random.normal(0.20, 0.05))
        new_store_repeat = int(new_store_new * repeat_rate)
        
        # Generate new customers for the new store
        new_store_customer_ids = []
        new_store_records = []
        for _ in range(new_store_new):
            rec = make_customer_record(new_loc, year, next_customer_id, next_order_id, is_new_store=True)
            new_store_records.append(rec)
            new_store_customer_ids.append(next_customer_id)
            next_customer_id += 1
            next_order_id += 1
        
        year_records.extend(new_store_records)
        
        # Generate repeat orders by sampling from the new store's own customers
        if new_store_repeat > 0 and len(new_store_records) > 0:
            new_store_df = pd.DataFrame(new_store_records)
            sampled_rows = new_store_df.sample(n=new_store_repeat, replace=True)
            for _, sampled_customer in sampled_rows.iterrows():
                rec = make_repeat_order(sampled_customer, year, next_order_id)
                year_records.append(rec)
                next_order_id += 1
        
        # Set baselines for the new store going forward
        running_loc_unique[new_loc] = new_store_new
        running_loc_orders[new_loc] = new_store_new + new_store_repeat
        
        print(f"    {new_loc} (NEW STORE): {new_store_new} new + {new_store_repeat} repeat = {new_store_new + new_store_repeat} orders")
    
    # Add this year's records to the pool for future repeat sampling
    year_df = pd.DataFrame(year_records)
    year_df['_Date'] = pd.to_datetime(year_df['Date'], errors='coerce')
    pool_df = pd.concat([pool_df, year_df], ignore_index=True)
    
    all_new_records.extend(year_records)
    
    year_total = len(year_records)
    print(f"\n    ✓ Year {year} total: {year_total} records")

print(f"\n✓ Total new records: {len(all_new_records)}")


# ============================================================================
# EMPLOYEE ASSIGNMENT
# ============================================================================

print("\n[STEP 5] Assigning employees to orders...")

new_customers_df = pd.DataFrame(all_new_records)
new_customers_df['Date'] = pd.to_datetime(new_customers_df['Date'])
new_customers_df = new_customers_df.sort_values(by='Date', ascending=True).reset_index(drop=True)

employees_orig['StartDate'] = pd.to_datetime(employees_orig['StartDate'])
employees_orig['TerminationDate'] = pd.to_datetime(employees_orig['TerminationDate'])
new_employees_df = employees_orig.copy()

print(f"  Starting with {len(new_employees_df)} existing employees...")

# Pre-staff new stores
print(f"\n  Pre-staffing new stores...")
for year in YEARS_TO_GENERATE:
    if year in NEW_STORES:
        new_employees_df = prestaff_new_store(
            NEW_STORES[year]['location'],
            year,
            NEW_STORES[year]['employees_needed'],
            new_employees_df
        )

# Assign employees to each order
employee_assignments = []
for idx, row in new_customers_df.iterrows():
    emp_id, new_employees_df = assign_employee(row, new_employees_df)
    employee_assignments.append(emp_id)
    
    if (idx + 1) % 1000 == 0:
        print(f"    Processed {idx + 1}/{len(new_customers_df)} orders...")

new_customers_df['EmployeeID'] = employee_assignments

nan_employees = new_customers_df['EmployeeID'].isna().sum()
total_employees = len(new_employees_df)
new_employees_created = total_employees - len(employees_orig)

print(f"\n✓ Employee assignment complete!")
print(f"  - Orders with assigned employees: {len(new_customers_df) - nan_employees}")
print(f"  - Orders without employees: {nan_employees}")
print(f"  - Total employees now: {total_employees}")
print(f"  - New employees created: {new_employees_created}")


# ============================================================================
# DATA EXPORT
# ============================================================================

print("\n[STEP 6] Exporting data to files...")

original_max_employee_id = employees_orig['EmployeeID'].max()
new_employees_only = new_employees_df[new_employees_df['EmployeeID'] > original_max_employee_id]

customer_cols = [
    "CustomerID", "first_name", "last_name", "gender",
    "DOB", "LoyaltyMember", "EmailList", "Source"
]

order_cols = [
    "CustomerID", "LocationID", "Date", "Time", "EmployeeID", "OrderID"
]

try:
    new_employees_only.to_excel(
        './data_new/newEmployees.xlsx',
        sheet_name='Employees',
        index=False
    )
    new_employees_df.to_excel(
        './data_full/Employees.xlsx',
        sheet_name='Employees',
        index=False
    )
    print(f"✓ Exported {len(new_employees_only)} new employees to ./data_new/newEmployees.xlsx")
    
    new_customers_df[customer_cols].drop_duplicates().rename(columns={
        "CustomerID": "id"
    }).to_excel(
        './data_new/newCustomers.xlsx',
        sheet_name='Customers',
        index=False
    )
    unique_customers = new_customers_df[customer_cols].drop_duplicates().shape[0]
    print(f"✓ Exported {unique_customers} unique customers to ./data_new/newCustomers.xlsx")
    
    new_customers_df[order_cols].drop_duplicates(subset=["CustomerID", "OrderID"]).to_excel(
        './data_new/newOrderInfo.xlsx',
        sheet_name='OrderInfo',
        index=False
    )
    unique_orders = new_customers_df[order_cols].drop_duplicates(subset=["CustomerID", "OrderID"]).shape[0]
    print(f"✓ Exported {unique_orders} orders to ./data_new/newOrderInfo.xlsx")
    
except Exception as e:
    print(f"✗ ERROR during export: {e}")
    sys.exit(1)


# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("GENERATION COMPLETE!")
print("=" * 80)
print(f"Years Generated: {YEARS_TO_GENERATE}")
print(f"Existing Locations: {EXISTING_LOCATIONS}")
print(f"New Locations Created: {[v['location'] for v in NEW_STORES.values()]}")
print(f"New Customers: {unique_customers}")
print(f"Total Orders: {unique_orders}")
print(f"New Employees: {len(new_employees_only)}")
print(f"\nFiles saved to ./data_new/")
print("=" * 80)
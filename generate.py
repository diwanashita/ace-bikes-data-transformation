"""
Ace Bikes Data Generator - Extended Years
==========================================
Generates synthetic customer and employee data for specified years.

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
print("ACE BIKES DATA GENERATOR")
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

# Growth rates
NEW_CUSTOMER_GROWTH_RATE = 0.095  # 9.5% new customers per year
REPEAT_CUSTOMER_RATE = 0.005      # 0.5% repeat customers per year

# Employee settings
EMPLOYEE_GENDER_OPTIONS = ['Male', 'Female', 'Other']
EMPLOYEE_GENDER_WEIGHTS = [0.44, 0.45, 0.11]
TRAINING_PROB = 0.15  # 15% of new hires have prior training

# New store configuration (employees needed per new store)
NEW_STORE_EMPLOYEES = 5  # Default number of employees for new store


# ============================================================================
# DATA LOADING
# ============================================================================

print("\n[STEP 1] Loading existing data files...")

try:
    # Load customer and order data
    customers_orig = pd.read_excel('./data_original/Customers.xlsx')
    orderinfo_orig = pd.read_excel('./data_original/OrderInfo.xlsx')
    
    # Convert datetime to date
    customers_orig['DOB'] = customers_orig['DOB'].dt.date
    orderinfo_orig['Date'] = orderinfo_orig['Date'].dt.date
    
    print(f"✓ Loaded {len(customers_orig)} customers")
    print(f"✓ Loaded {len(orderinfo_orig)} orders")
    
    # Load employee data from multiple sources
    employees_prof_orig = pd.read_excel('./data_original/Employees.xlsx')
    employees_dates_orig = pd.read_excel('./data_original/Ace_Bikes_Data.xlsx', 
                                         usecols=['EmployeeID', 'StartDate', 'TerminationDate', 'LocationID'])
    
    # Convert employee dates
    employees_prof_orig['DOB'] = employees_prof_orig['DOB'].dt.date
    employees_dates_orig['StartDate'] = employees_dates_orig['StartDate'].dt.date
    employees_dates_orig['TerminationDate'] = employees_dates_orig['TerminationDate'].dt.date
    
    # Merge employee data
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

# Get existing locations from the data
EXISTING_LOCATIONS = sorted(orderinfo_orig['LocationID'].dropna().unique().tolist())
print(f"✓ Found {len(EXISTING_LOCATIONS)} existing locations: {EXISTING_LOCATIONS}")

# Function to generate new store location ID
def generate_next_location_id(existing_locations):
    """
    Generate the next location ID based on existing pattern.
    Assumes pattern like L01, L02, ..., L11, L012, L013, etc.
    """
    # Extract numeric parts from location IDs
    location_numbers = []
    for loc in existing_locations:
        # Remove 'L' prefix and convert to int
        num_str = loc.replace('L', '').replace('l', '')
        try:
            location_numbers.append(int(num_str))
        except ValueError:
            continue
    
    if location_numbers:
        next_num = max(location_numbers) + 1
        # Format with leading zeros if pattern suggests it
        if next_num < 10:
            return f"L0{next_num}"
        else:
            return f"L{next_num}"
    else:
        return "L01"  # Fallback

# Generate new stores dynamically for each year to be generated
NEW_STORES = {}
current_locations = EXISTING_LOCATIONS.copy()

for year in YEARS_TO_GENERATE:
    # Generate a new store for each year starting from baseline
    if year >= BASELINE_YEAR:
        new_location = generate_next_location_id(current_locations)
        
        # Last year gets one extra employee (arbitrary business rule)
        employees_needed = NEW_STORE_EMPLOYEES + 1 if year == YEARS_TO_GENERATE[-1] else NEW_STORE_EMPLOYEES
        
        NEW_STORES[year] = {
            'location': new_location,
            'employees_needed': employees_needed
        }
        current_locations.append(new_location)

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
next_order_id = customer_order_df['OrderID'].max() + 1
next_customer_id = customer_order_df['CustomerID'].max() + 1
next_employee_id = employees_orig['EmployeeID'].max() + 1

# Calculate baseline customer count from specified year
customers_baseline = len(customer_order_df[customer_order_df['Date'] > date(BASELINE_YEAR - 1, 12, 31)])

print(f"✓ Next Customer ID: {next_customer_id}")
print(f"✓ Next Order ID: {next_order_id}")
print(f"✓ Next Employee ID: {next_employee_id}")
print(f"✓ Baseline customers ({BASELINE_YEAR}): {customers_baseline}")


# ============================================================================
# CUSTOMER GENERATION FUNCTIONS
# ============================================================================

def generate_new_customers(year, num_customers, next_customer_id, next_order_id, all_locations, new_stores_dict):
    """
    Generate brand new customers for a given year.
    
    Args:
        year: Year to generate customers for
        num_customers: Number of new customers to create
        next_customer_id: Starting customer ID
        next_order_id: Starting order ID
        all_locations: List of available store locations
        new_stores_dict: Dictionary of new stores by year
        
    Returns:
        tuple: (list of new customer dicts, updated next_customer_id, updated next_order_id)
    """
    new_customers = []
    
    # Check if a new store opened this year
    new_store = new_stores_dict.get(year)
    
    # Allocate 20% of new customers to new store if it exists
    if new_store:
        new_store_customers = int(num_customers * 0.20)
        regular_customers = num_customers - new_store_customers
    else:
        new_store_customers = 0
        regular_customers = num_customers
    
    # Generate regular customers across existing locations
    for i in range(regular_customers):
        # Random date within the year
        day_of_year = np.random.randint(1, 366)
        customer_date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
        
        # Random time during business hours (9 AM - 6 PM)
        hour = np.random.randint(9, 18)
        minute = np.random.randint(0, 60)
        second = np.random.randint(0, 60)
        customer_time = f"{hour:02d}:{minute:02d}:{second:02d}"
        
        # Generate demographic data
        dob = fake.date_of_birth(minimum_age=18, maximum_age=71)
        gender = np.random.choice(GENDER_OPTIONS, p=GENDER_WEIGHTS)
        
        # Generate name based on gender
        if gender == 'M':
            first_name = fake.first_name_male()
        elif gender == 'F':
            first_name = fake.first_name_female()
        else:
            first_name = fake.first_name_nonbinary()
        last_name = fake.last_name()
        
        # Loyalty program membership (35% are members)
        loyalty_member = np.random.choice([0.0, 1.0], p=[0.65, 0.35])
        
        # Email list subscription (correlated with loyalty membership)
        if loyalty_member == 1.0:
            email_list = np.random.choice([0.0, 1.0], p=[0.30, 0.70])
        else:
            email_list = np.random.choice([0.0, 1.0], p=[0.70, 0.30])
        
        # Customer acquisition source
        source = np.random.choice(SOURCE_OPTIONS, p=SOURCE_WEIGHTS)
        
        # Location (exclude new stores that opened this year)
        new_locations_this_year = [item['location'] for y, item in new_stores_dict.items() if y == year]
        available_locs = [loc for loc in all_locations if loc not in new_locations_this_year]
        location = np.random.choice(available_locs) if available_locs else np.random.choice(all_locations)
        
        new_customer = {
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
            'EmployeeID': None,  # Assigned later
            'OrderID': next_order_id
        }
        
        new_customers.append(new_customer)
        next_customer_id += 1
        next_order_id += 1
    
    # Generate new store customers (if applicable)
    if new_store and new_store_customers > 0:
        new_store_location = new_store['location']
        
        for i in range(new_store_customers):
            # 70% of customers arrive in first 3 months (opening spike)
            if i < int(new_store_customers * 0.70):
                month = np.random.randint(1, 4)  # Jan-Mar
            else:
                month = np.random.randint(4, 13)  # Apr-Dec
            
            day = np.random.randint(1, 29)
            customer_date = datetime(year, month, day)
            
            # Random time during extended hours (9 AM - 9 PM for new store)
            hour = np.random.randint(9, 21)
            minute = np.random.randint(0, 60)
            second = np.random.randint(0, 60)
            customer_time = f"{hour:02d}:{minute:02d}:{second:02d}"
            
            # Generate demographic data
            dob = fake.date_of_birth(minimum_age=18, maximum_age=71)
            gender = np.random.choice(GENDER_OPTIONS, p=GENDER_WEIGHTS)
            
            # Generate name
            if gender == 'M':
                first_name = fake.first_name_male()
            elif gender == 'F':
                first_name = fake.first_name_female()
            else:
                first_name = fake.first_name_nonbinary()
            last_name = fake.last_name()
            
            # Higher loyalty rate for new store (grand opening promotion - 50%)
            loyalty_member = np.random.choice([0.0, 1.0], p=[0.50, 0.50])
            
            # Email list (higher correlation for new store)
            if loyalty_member == 1.0:
                email_list = np.random.choice([0.0, 1.0], p=[0.20, 0.80])
            else:
                email_list = np.random.choice([0.0, 1.0], p=[0.60, 0.40])
            
            # Source (more walk-in and advertisement for new store)
            new_store_sources = ['Newspaper', 'Social', 'Referral', 'WalkIn', 'Online', 'Advertisement']
            new_store_weights = [0.05, 0.20, 0.10, 0.35, 0.10, 0.20]
            source = np.random.choice(new_store_sources, p=new_store_weights)
            
            new_customer = {
                'CustomerID': next_customer_id,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'DOB': dob.strftime('%Y-%m-%d'),
                'LoyaltyMember': loyalty_member,
                'EmailList': email_list,
                'Source': source,
                'LocationID': new_store_location,
                'Date': customer_date.strftime('%Y-%m-%d'),
                'Time': customer_time,
                'EmployeeID': None,
                'OrderID': next_order_id
            }
            
            new_customers.append(new_customer)
            next_customer_id += 1
            next_order_id += 1
    
    return new_customers, next_customer_id, next_order_id


def generate_duplicate_customers(year, num_customers, next_order_id, customer_df):
    """
    Generate repeat orders for existing customers.
    
    Args:
        year: Year to generate orders for
        num_customers: Number of repeat orders to create
        next_order_id: Starting order ID
        customer_df: DataFrame of existing customers to sample from
        
    Returns:
        tuple: (list of repeat order dicts, updated next_order_id)
    """
    new_orders = []
    
    for i in range(num_customers):
        # Sample a random existing customer
        sampled_customer = customer_df.sample(n=1).iloc[0]
        
        # Generate new date within the specified year
        day_of_year = np.random.randint(1, 366)
        order_date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
        
        # Random time during business hours (9 AM - 8 PM)
        hour = np.random.randint(9, 21)
        minute = np.random.randint(0, 60)
        second = np.random.randint(0, 60)
        order_time = f"{hour:02d}:{minute:02d}:{second:02d}"
        
        # Create repeat order with existing customer info
        repeat_order = {
            'CustomerID': sampled_customer['CustomerID'],
            'first_name': sampled_customer['first_name'],
            'last_name': sampled_customer['last_name'],
            'gender': sampled_customer['gender'],
            'DOB': sampled_customer['DOB'],
            'LoyaltyMember': sampled_customer['LoyaltyMember'],
            'EmailList': sampled_customer['EmailList'],
            'Source': sampled_customer['Source'],
            'LocationID': sampled_customer['LocationID'],  # Keep usual location
            'Date': order_date.strftime('%Y-%m-%d'),
            'Time': order_time,
            'EmployeeID': None,  # Assigned later
            'OrderID': next_order_id
        }
        
        new_orders.append(repeat_order)
        next_order_id += 1
    
    return new_orders, next_order_id


# ============================================================================
# EMPLOYEE MANAGEMENT FUNCTIONS
# ============================================================================

def create_new_employee(location, year, new_employees_df):
    """
    Create a new employee for a specific location and year.
    
    Args:
        location: Store location ID
        year: Year of hire
        new_employees_df: DataFrame of employees (modified in place)
        
    Returns:
        int: The new employee's ID
    """
    global next_employee_id
    
    # Generate demographic data
    gender = np.random.choice(EMPLOYEE_GENDER_OPTIONS, p=EMPLOYEE_GENDER_WEIGHTS)
    
    # Generate name based on gender
    if gender == 'Male':
        first_name = fake.first_name_male()
    elif gender == 'Female':
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Generate DOB (age between 20-50)
    dob = fake.date_of_birth(minimum_age=20, maximum_age=50)
    
    # Start date at beginning of year (early January)
    start_date = pd.Timestamp(f"{year}-01-{np.random.randint(1, 5):02d}")
    
    # Create employee record
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
    
    # Add to employee dataframe
    new_employee_df = pd.DataFrame([new_employee])
    new_employees_df = pd.concat([new_employees_df, new_employee_df], ignore_index=True)
    
    employee_id = next_employee_id
    next_employee_id += 1
    
    return employee_id, new_employees_df


def assign_employee(row, new_employees_df):
    """
    Assign an employee to an order based on location, date, and availability.
    
    Args:
        row: DataFrame row containing order information
        new_employees_df: DataFrame of employees (modified in place for terminations)
        
    Returns:
        int: Assigned employee ID
    """
    # If employee already assigned, return it
    if pd.notna(row["EmployeeID"]):
        return row['EmployeeID'], new_employees_df
    
    order_date = pd.Timestamp(row['Date'])
    order_year = order_date.year
    location = row['LocationID']
    
    # Handle malformed LocationID
    if isinstance(location, dict):
        location = location.get('location', None)
    
    if location is None or pd.isna(location):
        return None, new_employees_df
    
    # Find eligible employees at this location on this date
    eligible = new_employees_df[new_employees_df['LocationID'] == location]
    eligible = eligible[eligible['StartDate'] <= order_date]
    eligible = eligible[
        (eligible['TerminationDate'].isna()) | 
        (eligible['TerminationDate'] > order_date)
    ]
    
    # 99.5% of the time, use existing employee; 0.5% create new
    use_existing = np.random.random() < 0.995
    
    if len(eligible) > 0 and use_existing:
        # Use existing employee
        return np.random.choice(eligible['EmployeeID'].values), new_employees_df
    else:
        # Small chance of termination (25%) when creating new employee
        if not use_existing and len(eligible) > 0 and np.random.random() < 0.25:
            emp_to_terminate = np.random.choice(eligible['EmployeeID'].values)
            termination_date = order_date - pd.Timedelta(days=np.random.randint(7, 30))
            new_employees_df.loc[
                new_employees_df['EmployeeID'] == emp_to_terminate,
                'TerminationDate'
            ] = termination_date
        
        # Create new employee
        employee_id, new_employees_df = create_new_employee(location, order_year, new_employees_df)
        return employee_id, new_employees_df


# ============================================================================
# MAIN GENERATION LOGIC
# ============================================================================

print("\n[STEP 4] Generating new customers...")

all_new_customers = []
current_baseline = customers_baseline

# Generate new customers for each year
for year in YEARS_TO_GENERATE:
    print(f"\n  Year {year}:")
    
    # Calculate number of new customers (growth rate applied)
    new_customer_count = int(current_baseline * NEW_CUSTOMER_GROWTH_RATE)
    
    # Update locations to include stores opened up to this year
    current_locations = EXISTING_LOCATIONS.copy()
    for y in range(YEARS_TO_GENERATE[0], year + 1):
        if y in NEW_STORES:
            current_locations.append(NEW_STORES[y]['location'])
    
    # Display generation info
    print(f"    - Target new customers: {new_customer_count}")
    if year in NEW_STORES:
        print(f"    - New store opening: {NEW_STORES[year]['location']}")
        print(f"    - New store customers: {int(new_customer_count * 0.20)}")
        print(f"    - Regular customers: {int(new_customer_count * 0.80)}")
    
    # Generate new customers
    year_customers, next_customer_id, next_order_id = generate_new_customers(
        year,
        new_customer_count,
        next_customer_id,
        next_order_id,
        current_locations,
        NEW_STORES
    )
    
    all_new_customers.extend(year_customers)
    
    # Update baseline for next year
    current_baseline += new_customer_count
    
    print(f"    ✓ Generated {len(year_customers)} new customers")

print(f"\n✓ Total new customers: {len(all_new_customers)}")


# ============================================================================
# GENERATE REPEAT ORDERS
# ============================================================================

print("\n[STEP 5] Generating repeat customer orders...")

# Convert new customers to DataFrame for sampling
new_customers_temp_df = pd.DataFrame(all_new_customers)
current_baseline = customers_baseline

# Generate repeat orders for years after baseline
for year in YEARS_TO_GENERATE[1:]:  # Skip first year
    # Calculate number of repeat orders
    repeat_order_count = int(current_baseline * REPEAT_CUSTOMER_RATE)
    
    print(f"\n  Year {year}: Generating {repeat_order_count} repeat orders")
    
    # Generate repeat orders
    repeat_orders, next_order_id = generate_duplicate_customers(
        year,
        repeat_order_count,
        next_order_id,
        new_customers_temp_df
    )
    
    all_new_customers.extend(repeat_orders)
    
    print(f"    ✓ Generated {len(repeat_orders)} repeat orders")

print(f"\n✓ Total orders (new + repeat): {len(all_new_customers)}")


# ============================================================================
# EMPLOYEE ASSIGNMENT
# ============================================================================

print("\n[STEP 6] Assigning employees to orders...")

# Convert to DataFrame and prepare for employee assignment
new_customers_df = pd.DataFrame(all_new_customers)
new_customers_df['Date'] = pd.to_datetime(new_customers_df['Date'])
new_customers_df = new_customers_df.sort_values(by='Date', ascending=True).reset_index(drop=True)

# Prepare employee DataFrame
employees_orig['StartDate'] = pd.to_datetime(employees_orig['StartDate'])
employees_orig['TerminationDate'] = pd.to_datetime(employees_orig['TerminationDate'])
new_employees_df = employees_orig.copy()

print(f"  Starting with {len(new_employees_df)} existing employees...")

# Assign employees to each order
employee_assignments = []
for idx, row in new_customers_df.iterrows():
    emp_id, new_employees_df = assign_employee(row, new_employees_df)
    employee_assignments.append(emp_id)
    
    # Progress indicator
    if (idx + 1) % 1000 == 0:
        print(f"    Processed {idx + 1}/{len(new_customers_df)} orders...")

new_customers_df['EmployeeID'] = employee_assignments

# Summary statistics
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

print("\n[STEP 7] Exporting data to files...")

# Get only newly created employees
original_max_employee_id = employees_orig['EmployeeID'].max()
new_employees_only = new_employees_df[new_employees_df['EmployeeID'] > original_max_employee_id]

# Define column sets
customer_cols = [
    "CustomerID",
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
    "OrderID"
]

# Export files
try:
    # Export new employees
    new_employees_only.to_excel(
        './data_new/newEmployees.xlsx',
        sheet_name='Employees',
        index=False
    )
    print(f"✓ Exported {len(new_employees_only)} new employees to ./data_new/newEmployees.xlsx")
    
    # Export new customers (deduplicated)
    new_customers_df[customer_cols].drop_duplicates().rename(columns={
        "CustomerID": "id"
    }).to_excel(
        './data_new/newCustomers.xlsx',
        sheet_name='Customers',
        index=False
    )
    unique_customers = new_customers_df[customer_cols].drop_duplicates().shape[0]
    print(f"✓ Exported {unique_customers} unique customers to ./data_new/newCustomers.xlsx")
    
    # Export order info (deduplicated)
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
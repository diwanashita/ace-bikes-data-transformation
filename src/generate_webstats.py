"""
WebStats Data Generator for Ace Bikes - Modular Version
Generates realistic web analytics data for configurable year ranges
"""
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import random


# Initialize
random.seed(1234)
np.random.seed(1234)


def calculate_sessions(year, start_year, base_sessions, growth_rate):
    """
    Calculate number of sessions for a given year based on growth pattern
    
    Parameters:
    -----------
    year : int
        Target year
    start_year : int
        Starting year
    base_sessions : int
        Number of sessions in the start year
    growth_rate : float
        Growth rate (e.g., 1.5 for 50% growth)
    
    Returns:
    --------
    int
        Number of sessions for the year
    """
    years_elapsed = year - start_year
    sessions = int(base_sessions * (growth_rate ** years_elapsed))
    return sessions


def calculate_mobile_share(year, start_year, base_mobile_share, mobile_growth_rate):
    """
    Calculate mobile device share for a given year
    
    Parameters:
    -----------
    year : int
        Target year
    start_year : int
        Starting year
    base_mobile_share : float
        Mobile share in start year (0-1)
    mobile_growth_rate : float
        Annual increase in mobile share (e.g., 0.03 for 3% per year)
    
    Returns:
    --------
    dict
        Device distribution for the year
    """
    years_elapsed = year - start_year
    mobile_share = min(0.75, base_mobile_share + (mobile_growth_rate * years_elapsed))
    
    # Fixed tablet share, remainder goes to desktop
    tablet_share = 0.10
    desktop_share = 1.0 - mobile_share - tablet_share
    
    return {
        'mobile': round(mobile_share, 2),
        'desktop': round(desktop_share, 2),
        'tablet': tablet_share
    }


def calculate_conversion_rate(year, start_year, base_conversion, conversion_improvement):
    """
    Calculate base conversion rate for a given year
    
    Parameters:
    -----------
    year : int
        Target year
    start_year : int
        Starting year
    base_conversion : float
        Base conversion rate in start year
    conversion_improvement : float
        Annual improvement in conversion rate
    
    Returns:
    --------
    float
        Base conversion rate for the year
    """
    years_elapsed = year - start_year
    return base_conversion + (conversion_improvement * years_elapsed)


def generate_webstats(year, num_sessions, device_distribution, base_conversion_rate):
    """
    Generate WebStats data for a given year
    
    Parameters:
    -----------
    year : int
        Year for the data
    num_sessions : int
        Number of sessions to generate
    device_distribution : dict
        Distribution of device types
    base_conversion_rate : float
        Base conversion rate for the year
    
    Returns:
    --------
    pandas.DataFrame
        WebStats data with all required columns
    """
    
    data = []
    
    for user_id in range(1, num_sessions + 1):
        # Generate device type based on year-specific distribution
        device_type = np.random.choice(
            list(device_distribution.keys()), 
            p=list(device_distribution.values())
        )
        
        # Generate browser 
        browser = np.random.choice(
            ['Chrome', 'Safari', 'Firefox', 'Edge'],
            p=[0.26, 0.25, 0.25, 0.24]
        )
        
        # Generate page views (most sessions have fewer pages)
        if random.random() < 0.7:
            page_views = random.randint(50, 3000)
        else:
            page_views = random.randint(3000, 10000)
        
        # Generate time on page (seconds)
        time_on_page = random.randint(40, 3500)
        
        # Generate conversion rate with high variance
        conversion_rate = base_conversion_rate + np.random.uniform(-40, 40)
        conversion_rate = np.clip(conversion_rate, 0, 100)
        conversion_rate = round(conversion_rate, 2)
        
        # Generate bounce rate
        bounce_rate = round(np.random.uniform(0, 95), 2)
        
        # Generate date within the year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        days_in_year = (end_date - start_date).days + 1
        random_days = random.randint(0, days_in_year - 1)
        date_visited = start_date + timedelta(days=random_days)
        date_visited_str = date_visited.strftime("%-m/%-d/%Y")
        
        # Generate time of day
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        period = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        time_of_day = f"{display_hour}:{minute:02d} {period}"
        
        # Append row
        data.append({
            'user_id': user_id,
            'page_views': page_views,
            'time_on_page': time_on_page,
            'device_type': device_type,
            'browser': browser,
            'conversion_rate': conversion_rate,
            'bounce_rate': bounce_rate,
            'date_visited': date_visited_str,
            'time_of_day_visited': time_of_day
        })
    
    return pd.DataFrame(data)


def main(start_year=2023, num_years=3, output_dir='./data_full/WebStats/'):
    """
    Generate WebStats files for specified year range
    
    Parameters:
    -----------
    start_year : int
        First year to generate data for (default: 2023)
    num_years : int
        Number of years to generate (default: 3)
    output_dir : str
        Directory to save files (default: './data_full/WebStats/')
    
    Configuration:
    --------------
    Historical pattern (for reference):
    - 2017: 500 sessions
    - 2018: 900 sessions
    - 2019: 1500 sessions
    - 2020: 2000 sessions
    - 2021: 3000 sessions
    - 2022: 4000 sessions
    
    Growth parameters are calibrated to continue this pattern
    """
    
    # ============================================================================
    # CONFIGURATION PARAMETERS - Adjust these to modify growth patterns
    # ============================================================================
    
    # Sessions growth configuration
    # Based on historical data: 2022 had 4000 sessions
    base_sessions_2022 = 4000
    sessions_growth_rate = 1.20  # ~37.5% annual growth (4000->5500->7500->10000)
    
    # Mobile share configuration
    # Mobile share increases over time: 2022 ~57% -> 2023 60% -> 2024 63% -> 2025 65%
    base_mobile_share_2022 = 0.57
    mobile_annual_growth = 0.03  # 3% increase per year
    
    # Conversion rate configuration
    # Slight improvement over time: 2022 ~52% -> 2023 53% -> 2024 54% -> 2025 55%
    base_conversion_2022 = 52
    conversion_annual_improvement = 1.0  # 1% improvement per year
    
    # ============================================================================
    
    print(f"Generating WebStats data for {num_years} years starting from {start_year}")
    print("=" * 70)
    
    for i in range(num_years):
        year = start_year + i
        
        # Calculate year-specific parameters
        num_sessions = calculate_sessions(
            year, 
            start_year=2022,
            base_sessions=base_sessions_2022,
            growth_rate=sessions_growth_rate
        )
        
        device_distribution = calculate_mobile_share(
            year,
            start_year=2022,
            base_mobile_share=base_mobile_share_2022,
            mobile_growth_rate=mobile_annual_growth
        )
        
        base_conversion = calculate_conversion_rate(
            year,
            start_year=2022,
            base_conversion=base_conversion_2022,
            conversion_improvement=conversion_annual_improvement
        )
        
        print(f"\nYear {year}:")
        print(f"  Sessions: {num_sessions:,}")
        print(f"  Device distribution: Mobile {device_distribution['mobile']:.1%}, "
              f"Desktop {device_distribution['desktop']:.1%}, "
              f"Tablet {device_distribution['tablet']:.1%}")
        print(f"  Base conversion rate: {base_conversion:.1f}%")
        
        # Generate data
        df = generate_webstats(year, num_sessions, device_distribution, base_conversion)
        
        # Save to CSV
        filename = f"WebStats{year}.csv"
        df.to_csv(f'{output_dir}{filename}', index=False)
        df.to_csv(f'./data_new/WebStats/{filename}', index=False)
        
        print(f"  ✓ Created {filename}")
    
    print("\n" + "=" * 70)
    print("All files generated successfully!")


if __name__ == "__main__":
    # Example usage:
    # Generate data for 2023-2025 (default)
    parser = argparse.ArgumentParser(description="Generate Reviews CSV files.")
    parser.add_argument("start_year", type=int, help="Start year (e.g., 2023)")
    parser.add_argument("no_years", type=int, help="Number of years to generate (e.g., 4)")
    args = parser.parse_args()

    full_webstats_dir = Path("./data_full/WebStats")
    full_webstats_dir.mkdir(parents=True, exist_ok=True)

    new_webstats_dir = Path("./data_new/WebStats")
    new_webstats_dir.mkdir(parents=True, exist_ok=True)

    start_year = args.start_year
    no_years = args.no_years
    main(start_year=start_year, num_years=no_years)
    
    # Generate data for different year range:
    # main(start_year=2026, num_years=5)
    
    # Generate with custom output directory:
    # main(start_year=2023, num_years=3, output_dir='./output/')
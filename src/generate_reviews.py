# imports
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import random

# Initialize random seeds for reproducibility
random.seed(1234)
np.random.seed(1234)



reviews_by_year_master = {
    2017: 209,
    2018: 776,
    2019: 1298,
    2020: 2088,
    2021: 2878,
    2022: 2919,
    2023: 3100,
    2024: 3300,
    2025: 3500,
    2026: 3600,
    2027: 3700,
    2028: 3800,
    2029: 3900,
    2030: 4000,
    2031: 4050,
    2032: 4100,
    2033: 4150,
    2034: 4200,
    2035: 4250,
    2036: 4300,
    2037: 4350
}


def generate_reviews_master_map(start_year, num_years):
    if start_year + num_years not in reviews_by_year_master:
        for i in range(2031, start_year + num_years):
            reviews_by_year_master[i] = reviews_by_year_master[i-1] + 50
    
    return reviews_by_year_master

def generate_reviews(year, num_reviews):
    """
    Generate Reviews data for a given year
    
    Parameters:
    -----------
    year : int
        Year for the data (2023, 2024, or 2025)
    num_reviews : int
        Number of reviews to generate
    
    Returns:
    --------
    pandas.DataFrame
        Reviews data with Date, Rating, and Platform columns
    """
    
    # Platform distribution: Facebook > Yelp > Google
    platform_probs = {
        'Facebook': 0.35,
        'Yelp': 0.34,
        'Google': 0.31
    }
    
    # Rating distribution (6-10 scale, skewed toward higher ratings)
    # More weight on 8, 9, 10
    rating_probs = {
        6: 0.10,
        7: 0.15,
        8: 0.25,
        9: 0.30,
        10: 0.20
    }
    
    data = []
    
    # Date range for the year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    days_in_year = (end_date - start_date).days + 1
    
    for _ in range(num_reviews):
        # Generate random date within the year
        random_days = random.randint(0, days_in_year - 1)
        date_reviewed = start_date + timedelta(days=random_days)
        date_str = date_reviewed.strftime("%-m/%-d/%Y")
        
        # Generate rating based on distribution
        rating = np.random.choice(
            list(rating_probs.keys()),
            p=list(rating_probs.values())
        )
        
        # Generate platform based on distribution
        platform = np.random.choice(
            list(platform_probs.keys()),
            p=list(platform_probs.values())
        )
        
        data.append({
            'Date': date_str,
            'Rating': rating,
            'Platform': platform
        })
    
    # Create DataFrame and sort by date
    df = pd.DataFrame(data)
    df['date_sort'] = pd.to_datetime(df['Date'])
    df = df.sort_values('date_sort').drop('date_sort', axis=1).reset_index(drop=True)
    
    return df


def main():
    """Generate Reviews files for 2023, 2024, and 2025"""
    
    # Review counts following the pattern
    # 2017=209, 2018=776, 2019=1298, 2020=2088, 2021=2878, 2022=2919
    # Continuing the growth (slowing down as maturity increases):
    # 2023=3100, 2024=3300, 2025=3500

    parser = argparse.ArgumentParser(description="Generate Reviews CSV files.")
    parser.add_argument("start_year", type=int, help="Start year (e.g., 2023)")
    parser.add_argument("no_years", type=int, help="Number of years to generate (e.g., 4)")
    args = parser.parse_args()

    full_reviews_dir = Path("./data_full/Reviews")
    full_reviews_dir.mkdir(parents=True, exist_ok=True)

    new_reviews_dir = Path("./data_new/Reviews")
    new_reviews_dir.mkdir(parents=True, exist_ok=True)

    start_year = args.start_year
    no_years = args.no_years
    
    reviews_by_year_master = generate_reviews_master_map(start_year, no_years)

    for i in range(start_year, start_year + no_years):
        year = i
        num_reviews = reviews_by_year_master[year]
        print(f"Generating {year}reviews.csv with {num_reviews:,} reviews...")
        
        # Generate data
        df = generate_reviews(year, num_reviews)
        
        # Save to CSV
        filename = f"{year}reviews.csv"

        df.to_csv(f'./data_full/Reviews/{filename}', index=False)
        df.to_csv(f'./data_new/Reviews/{filename}', index=False)
        
        # Print summary statistics
        print(f"  ✓ Created {filename}")
        print(f"    - Total reviews: {len(df):,}")
        
        # Platform distribution
        platform_counts = df['Platform'].value_counts()
        for platform in ['Facebook', 'Yelp', 'Google']:
            count = platform_counts.get(platform, 0)
            pct = (count / len(df)) * 100
            print(f"    - {platform}: {count:,} ({pct:.1f}%)")
        
        # Rating distribution
        rating_counts = df['Rating'].value_counts().sort_index()
        avg_rating = df['Rating'].mean()
        print(f"    - Average rating: {avg_rating:.2f}")
        print(f"    - Rating distribution:", end="")
        for rating in sorted(df['Rating'].unique()):
            count = rating_counts.get(rating, 0)
            print(f" {rating}★:{count}", end="")
        print("\n")

if __name__ == "__main__":
    main()
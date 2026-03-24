"""
Ingest disease data from Our World in Data (OWID)
"""
import pandas as pd
import requests
from sqlalchemy import create_engine
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def download_owid_covid():
    """Download COVID-19 data from OWID"""
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    print("Downloading COVID-19 data from OWID...")
    df = pd.read_csv(url)
    return df

def process_and_load_covid(df):
    """Process and load COVID data into database"""
    print("Processing COVID-19 data...")

    # Select relevant columns
    columns = [
        'iso_code', 'location', 'date',
        'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
        'population'
    ]
    df = df[columns].copy()

    # Filter out non-country aggregates
    df = df[df['iso_code'].str.len() == 3]  # Country ISO codes are 3 letters

    # Convert date
    df['date'] = pd.to_datetime(df['date'])

    # Calculate rates per 100k
    df['incidence_rate'] = (df['total_cases'] / df['population']) * 100000
    df['mortality_rate'] = (df['total_deaths'] / df['population']) * 100000

    # Fill NaN with 0 for case/death counts
    df[['total_cases', 'new_cases', 'total_deaths', 'new_deaths']] = \
        df[['total_cases', 'new_cases', 'total_deaths', 'new_deaths']].fillna(0)

    print(f"Processed {len(df)} COVID-19 records")

    # Note: This is a simplified version. In production, you would:
    # 1. Match iso_code to region_id from regions table
    # 2. Get disease_id for COVID-19 from diseases table
    # 3. Insert into disease_records table

    return df

def main():
    print("Starting OWID COVID-19 data ingestion...")

    # Download data
    covid_df = download_owid_covid()

    # Process data
    processed_df = process_and_load_covid(covid_df)

    # Save to CSV for now (in production, insert into DB)
    output_file = "data/owid_covid_processed.csv"
    os.makedirs("data", exist_ok=True)
    processed_df.to_csv(output_file, index=False)
    print(f"Saved processed data to {output_file}")

    print("OWID ingestion complete!")

if __name__ == "__main__":
    main()

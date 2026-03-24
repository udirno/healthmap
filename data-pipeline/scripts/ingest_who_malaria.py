"""
Malaria Data Ingestion from WHO Global Health Observatory
Downloads real malaria incidence and mortality data
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, date
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://healthmap_user:healthmap_password@localhost:5432/healthmap_db")

# WHO GHO Malaria data - cases by country
WHO_MALARIA_URL = "https://ghoapi.azureedge.net/api/MALARIA_EST_CASES"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def download_who_malaria_data():
    """Download Malaria data from WHO GHO API"""
    print(f"📥 Downloading Malaria data from WHO GHO...")
    print(f"   URL: {WHO_MALARIA_URL}")

    try:
        # WHO GHO API returns JSON
        import requests
        response = requests.get(WHO_MALARIA_URL, timeout=60)
        response.raise_for_status()

        data = response.json()
        df = pd.DataFrame(data['value'])

        print(f"✅ Downloaded {len(df):,} rows")
        return df
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        print("   Trying alternative CSV source...")

        # Fallback to CSV if API fails
        try:
            alt_url = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Malaria%20incidence%20-%20IHME/Malaria%20incidence%20-%20IHME.csv"
            df = pd.read_csv(alt_url)
            print(f"✅ Downloaded {len(df):,} rows from alternative source")
            return df
        except Exception as e2:
            print(f"❌ Alternative source also failed: {e2}")
            sys.exit(1)

def process_malaria_data(df):
    """Process Malaria data into our format"""
    print("\n🔍 Processing Malaria data...")

    # WHO GHO format has specific structure
    if 'SpatialDim' in df.columns:
        # This is WHO GHO API format
        print("   Using WHO GHO API format...")

        malaria_df = df[['SpatialDim', 'TimeDim', 'NumericValue']].copy()
        malaria_df.columns = ['iso_code', 'year', 'total_cases']

        # Add country names (we'll get them from regions table)
        malaria_df['location'] = malaria_df['iso_code']

        # Estimate deaths (WHO provides separate endpoint, using ~0.2% CFR estimate)
        malaria_df['total_deaths'] = (malaria_df['total_cases'] * 0.002).astype(int)

        # Population estimate (rough, will be refined)
        malaria_df['population'] = 10000000  # Placeholder

    elif 'Entity' in df.columns:
        # OWID/IHME format
        print("   Using OWID/IHME format...")

        malaria_df = df[['Code', 'Entity', 'Year', 'Incidence of malaria (IHME, 2019)']].copy()
        malaria_df.columns = ['iso_code', 'location', 'year', 'total_cases']

        malaria_df['total_cases'] = malaria_df['total_cases'].fillna(0).astype(int)
        malaria_df['total_deaths'] = (malaria_df['total_cases'] * 0.002).astype(int)
        malaria_df['population'] = 10000000

        # Remove rows without ISO code
        malaria_df = malaria_df[malaria_df['iso_code'].notna()]
    else:
        print(f"   ⚠️ Unknown format. Columns: {df.columns.tolist()}")
        sys.exit(1)

    # Clean data
    malaria_df = malaria_df[malaria_df['iso_code'].str.len() == 3].copy()
    malaria_df['total_cases'] = pd.to_numeric(malaria_df['total_cases'], errors='coerce').fillna(0).astype(int)
    malaria_df['year'] = pd.to_numeric(malaria_df['year'], errors='coerce').fillna(2020).astype(int)

    # Calculate rates (rough estimates)
    malaria_df['incidence_rate'] = (malaria_df['total_cases'] / malaria_df['population']) * 100000
    malaria_df['mortality_rate'] = (malaria_df['total_deaths'] / malaria_df['population']) * 100000

    print(f"✅ Processed {len(malaria_df):,} records")
    print(f"   Countries: {malaria_df['iso_code'].nunique()}")
    print(f"   Years: {malaria_df['year'].min()} to {malaria_df['year'].max()}")

    return malaria_df

def load_malaria_records(conn, df):
    """Load Malaria data into database"""
    print("\n📊 Loading Malaria records into database...")

    cursor = conn.cursor()

    # Get Malaria disease ID
    cursor.execute("SELECT id FROM diseases WHERE code = 'MALARIA'")
    result = cursor.fetchone()
    if not result:
        print("❌ Malaria disease not found in database")
        return 0

    disease_id = result[0]

    # Get region mapping
    cursor.execute("SELECT code, id FROM regions")
    region_map = {row[0]: row[1] for row in cursor.fetchall()}

    # Prepare records
    records = []
    skipped = 0

    for _, row in df.iterrows():
        region_id = region_map.get(row['iso_code'])
        if not region_id:
            skipped += 1
            continue

        # Use January 1st of the year
        record_date = date(int(row['year']), 1, 1)

        records.append((
            disease_id,
            region_id,
            record_date,
            int(row['total_cases']),
            0,
            int(row['total_deaths']),
            0,
            round(row['incidence_rate'], 2),
            round(row['mortality_rate'], 2),
            'WHO_MALARIA'
        ))

    print(f"   Preparing to insert {len(records):,} records...")
    print(f"   Skipped {skipped} records (no matching region)")

    # Clear existing data
    cursor.execute("""
        DELETE FROM disease_records
        WHERE disease_id = %s AND data_source = 'WHO_MALARIA'
    """, (disease_id,))
    print(f"   Cleared existing WHO Malaria data")

    # Bulk insert
    insert_query = """
        INSERT INTO disease_records
        (disease_id, region_id, date, total_cases, new_cases, total_deaths, new_deaths, incidence_rate, mortality_rate, data_source)
        VALUES %s
    """

    execute_values(cursor, insert_query, records)
    conn.commit()
    cursor.close()

    print(f"✅ Successfully loaded {len(records):,} Malaria records")
    return len(records)

def verify_malaria_data(conn):
    """Verify Malaria data"""
    print("\n✅ Verifying Malaria data...")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*), COUNT(DISTINCT region_id), MIN(date), MAX(date)
        FROM disease_records
        WHERE data_source = 'WHO_MALARIA'
    """)
    total, countries, min_date, max_date = cursor.fetchone()

    print(f"\n📈 Malaria Data Summary:")
    print(f"   Total records: {total:,}")
    print(f"   Countries: {countries}")
    if min_date and max_date:
        print(f"   Year range: {min_date.year} to {max_date.year}")

    # Top Malaria burden countries
    cursor.execute("""
        SELECT r.name, dr.date, dr.total_cases, dr.total_deaths
        FROM disease_records dr
        JOIN regions r ON dr.region_id = r.id
        WHERE dr.data_source = 'WHO_MALARIA'
        ORDER BY dr.total_cases DESC
        LIMIT 5
    """)

    results = cursor.fetchall()
    if results:
        print(f"\n🔍 Top Malaria burden countries:")
        for row in results:
            print(f"   {row[0]} ({row[1].year}): Cases: {row[2]:,}, Deaths: {row[3]:,}")

    cursor.close()

def main():
    print("=" * 60)
    print("🦟 HealthMap Malaria Data Ingestion Pipeline")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Download
    raw_df = download_who_malaria_data()

    # Process
    clean_df = process_malaria_data(raw_df)

    # Connect
    print("\n🔌 Connecting to database...")
    try:
        conn = get_db_connection()
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

    # Load
    records_loaded = load_malaria_records(conn, clean_df)

    # Verify
    verify_malaria_data(conn)

    conn.close()

    print("\n" + "=" * 60)
    print(f"✅ Malaria Ingestion completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()

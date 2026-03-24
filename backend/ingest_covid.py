"""
Complete COVID-19 Data Ingestion from Our World in Data
Downloads real, up-to-date data and loads into PostgreSQL
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://healthmap_user:healthmap_password@localhost:5432/healthmap_db")

# OWID COVID-19 data URL (updated regularly)
OWID_COVID_URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)

def download_owid_data():
    """Download COVID-19 data from Our World in Data"""
    print(f"📥 Downloading COVID-19 data from OWID...")
    print(f"   URL: {OWID_COVID_URL}")

    try:
        df = pd.read_csv(OWID_COVID_URL)
        print(f"✅ Downloaded {len(df):,} rows")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   Unique locations: {df['location'].nunique()}")
        return df
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        sys.exit(1)

def filter_and_validate_data(df):
    """Filter to country-level data and validate"""
    print("\n🔍 Filtering and validating data...")

    # Keep only country-level data (ISO codes are 3 characters)
    # Exclude aggregates like 'World', 'Europe', etc.
    country_df = df[
        (df['iso_code'].str.len() == 3) &
        (~df['iso_code'].str.startswith('OWID'))
    ].copy()

    print(f"   Countries with data: {country_df['location'].nunique()}")

    # Select only columns we need
    columns_needed = [
        'iso_code', 'location', 'date',
        'total_cases', 'new_cases',
        'total_deaths', 'new_deaths',
        'population'
    ]

    country_df = country_df[columns_needed].copy()

    # Convert date
    country_df['date'] = pd.to_datetime(country_df['date']).dt.date

    # Fill NaN with 0 for case/death counts
    for col in ['total_cases', 'new_cases', 'total_deaths', 'new_deaths']:
        country_df[col] = country_df[col].fillna(0).astype(int)

    # Remove rows where population is missing
    country_df = country_df[country_df['population'].notna()]

    # Calculate rates per 100,000 population
    country_df['incidence_rate'] = (country_df['total_cases'] / country_df['population']) * 100000
    country_df['mortality_rate'] = (country_df['total_deaths'] / country_df['population']) * 100000

    print(f"✅ Validated {len(country_df):,} records")
    print(f"   Countries: {country_df['iso_code'].nunique()}")
    print(f"   Date range: {country_df['date'].min()} to {country_df['date'].max()}")

    return country_df

def load_regions(conn, df):
    """Load unique regions (countries) into database"""
    print("\n🌍 Loading regions into database...")

    cursor = conn.cursor()

    # Get unique countries
    countries = df[['iso_code', 'location', 'population']].drop_duplicates('iso_code')

    # Simple lat/long mapping for major countries (we'll expand this)
    country_coords = {
        'USA': (37.0902, -95.7129),
        'GBR': (55.3781, -3.4360),
        'FRA': (46.2276, 2.2137),
        'DEU': (51.1657, 10.4515),
        'ITA': (41.8719, 12.5674),
        'ESP': (40.4637, -3.7492),
        'BRA': (-14.2350, -51.9253),
        'IND': (20.5937, 78.9629),
        'CHN': (35.8617, 104.1954),
        'JPN': (36.2048, 138.2529),
        'KOR': (35.9078, 127.7669),
        'AUS': (-25.2744, 133.7751),
        'CAN': (56.1304, -106.3468),
        'MEX': (23.6345, -102.5528),
        'RUS': (61.5240, 105.3188),
        'ZAF': (-30.5595, 22.9375),
        'NGA': (9.0820, 8.6753),
        'EGY': (26.8206, 30.8025),
        'ARG': (-38.4161, -63.6167),
        'COL': (4.5709, -74.2973),
    }

    inserted = 0
    for _, row in countries.iterrows():
        iso_code = row['iso_code']
        lat, lon = country_coords.get(iso_code, (0, 0))

        try:
            cursor.execute("""
                INSERT INTO regions (name, code, level, latitude, longitude, population)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (code) DO UPDATE SET
                    population = EXCLUDED.population,
                    name = EXCLUDED.name
            """, (row['location'], iso_code, 'country', lat, lon, int(row['population'])))
            inserted += 1
        except Exception as e:
            print(f"   ⚠️ Error inserting {iso_code}: {e}")

    conn.commit()
    print(f"✅ Loaded {inserted} regions")

    # Build region ID mapping
    cursor.execute("SELECT code, id FROM regions")
    region_map = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()

    return region_map

def load_disease_records(conn, df, region_map):
    """Load COVID-19 case data into database"""
    print("\n📊 Loading disease records into database...")

    cursor = conn.cursor()

    # Get COVID-19 disease ID
    cursor.execute("SELECT id FROM diseases WHERE code = 'COVID19'")
    result = cursor.fetchone()
    if not result:
        print("❌ COVID-19 disease not found in database")
        return

    disease_id = result[0]

    # Prepare data for bulk insert
    records = []
    skipped = 0

    for _, row in df.iterrows():
        region_id = region_map.get(row['iso_code'])
        if not region_id:
            skipped += 1
            continue

        records.append((
            disease_id,
            region_id,
            row['date'],
            int(row['total_cases']),
            int(row['new_cases']),
            int(row['total_deaths']),
            int(row['new_deaths']),
            round(row['incidence_rate'], 2),
            round(row['mortality_rate'], 2),
            'OWID'
        ))

    print(f"   Preparing to insert {len(records):,} records...")
    print(f"   Skipped {skipped} records (no matching region)")

    # Bulk insert with conflict handling
    # First, clear existing COVID data to avoid duplicates
    cursor.execute("""
        DELETE FROM disease_records
        WHERE disease_id = %s AND data_source = 'OWID'
    """, (disease_id,))
    print(f"   Cleared existing OWID COVID-19 data")

    # Bulk insert
    insert_query = """
        INSERT INTO disease_records
        (disease_id, region_id, date, total_cases, new_cases, total_deaths, new_deaths, incidence_rate, mortality_rate, data_source)
        VALUES %s
    """

    # Insert in batches of 10000
    batch_size = 10000
    total_inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        execute_values(cursor, insert_query, batch)
        total_inserted += len(batch)
        print(f"   Inserted {total_inserted:,} / {len(records):,} records...")

    conn.commit()
    cursor.close()

    print(f"✅ Successfully loaded {total_inserted:,} disease records")

def log_ingestion(conn, source, disease, records_inserted, status, error=None):
    """Log the ingestion run"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO data_ingestion_log
        (source, disease, records_inserted, records_updated, started_at, completed_at, status, error_message)
        VALUES (%s, %s, %s, 0, NOW(), NOW(), %s, %s)
    """, (source, disease, records_inserted, status, error))
    conn.commit()
    cursor.close()

def verify_data(conn):
    """Verify the loaded data"""
    print("\n✅ Verifying loaded data...")

    cursor = conn.cursor()

    # Count records
    cursor.execute("SELECT COUNT(*) FROM disease_records WHERE data_source = 'OWID'")
    total_records = cursor.fetchone()[0]

    # Count countries
    cursor.execute("""
        SELECT COUNT(DISTINCT region_id)
        FROM disease_records
        WHERE data_source = 'OWID'
    """)
    total_countries = cursor.fetchone()[0]

    # Date range
    cursor.execute("""
        SELECT MIN(date), MAX(date)
        FROM disease_records
        WHERE data_source = 'OWID'
    """)
    min_date, max_date = cursor.fetchone()

    # Sample data
    cursor.execute("""
        SELECT r.name, dr.date, dr.total_cases, dr.new_cases, dr.total_deaths
        FROM disease_records dr
        JOIN regions r ON dr.region_id = r.id
        WHERE dr.data_source = 'OWID'
        ORDER BY dr.date DESC, dr.total_cases DESC
        LIMIT 5
    """)

    print(f"\n📈 Data Summary:")
    print(f"   Total records: {total_records:,}")
    print(f"   Countries covered: {total_countries}")
    print(f"   Date range: {min_date} to {max_date}")

    print(f"\n🔍 Sample recent data:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} - Cases: {row[2]:,}, Deaths: {row[4]:,}")

    cursor.close()

def main():
    print("=" * 60)
    print("🦠 HealthMap COVID-19 Data Ingestion Pipeline")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Download data
    raw_df = download_owid_data()

    # Filter and validate
    clean_df = filter_and_validate_data(raw_df)

    # Connect to database
    print("\n🔌 Connecting to database...")
    try:
        conn = get_db_connection()
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

    # Load data
    region_map = load_regions(conn, clean_df)
    load_disease_records(conn, clean_df, region_map)

    # Log the ingestion
    log_ingestion(conn, 'OWID', 'COVID-19', len(clean_df), 'success')

    # Verify
    verify_data(conn)

    conn.close()

    print("\n" + "=" * 60)
    print(f"✅ Ingestion completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()

"""
Tuberculosis Data Ingestion from WHO Global TB Programme
Downloads real TB incidence and mortality data
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

# WHO TB data - estimates by country
WHO_TB_URL = "https://extranet.who.int/tme/generateCSV.asp?ds=estimates"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def download_who_tb_data():
    """Download TB data from WHO"""
    print(f"📥 Downloading Tuberculosis data from WHO...")
    print(f"   URL: {WHO_TB_URL}")

    try:
        df = pd.read_csv(WHO_TB_URL, encoding='latin-1')
        print(f"✅ Downloaded {len(df):,} rows")
        print(f"   Years: {df['year'].min()} to {df['year'].max()}")
        print(f"   Countries: {df['country'].nunique()}")
        return df
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        sys.exit(1)

def process_tb_data(df):
    """Process TB data into our format"""
    print("\n🔍 Processing TB data...")

    # Select key columns
    # e_inc_num = estimated incidence (number)
    # e_mort_exc_tbhiv_num = estimated mortality excluding TB/HIV (number)
    columns_needed = ['iso3', 'country', 'year', 'e_inc_num', 'e_mort_exc_tbhiv_num', 'e_pop_num']

    # Check which columns exist
    available_cols = [col for col in columns_needed if col in df.columns]
    print(f"   Available columns: {available_cols}")

    if 'e_inc_num' not in df.columns:
        print("   ⚠️ Using alternative column names...")
        # Try alternative column names
        if 'inc_num' in df.columns:
            df['e_inc_num'] = df['inc_num']
        else:
            df['e_inc_num'] = 0

    if 'e_mort_exc_tbhiv_num' not in df.columns:
        if 'mort_num' in df.columns:
            df['e_mort_exc_tbhiv_num'] = df['mort_num']
        else:
            df['e_mort_exc_tbhiv_num'] = 0

    if 'e_pop_num' not in df.columns:
        df['e_pop_num'] = 1000000  # Default if not available

    tb_df = df[['iso3', 'country', 'year', 'e_inc_num', 'e_mort_exc_tbhiv_num', 'e_pop_num']].copy()

    # Rename columns
    tb_df.columns = ['iso_code', 'location', 'year', 'total_cases', 'total_deaths', 'population']

    # Fill NaN
    tb_df['total_cases'] = tb_df['total_cases'].fillna(0).astype(int)
    tb_df['total_deaths'] = tb_df['total_deaths'].fillna(0).astype(int)
    tb_df['population'] = tb_df['population'].fillna(1000000).astype(int)

    # Calculate rates per 100k
    tb_df['incidence_rate'] = (tb_df['total_cases'] / tb_df['population']) * 100000
    tb_df['mortality_rate'] = (tb_df['total_deaths'] / tb_df['population']) * 100000

    print(f"✅ Processed {len(tb_df):,} records")
    print(f"   Countries: {tb_df['iso_code'].nunique()}")
    print(f"   Years: {tb_df['year'].min()} to {tb_df['year'].max()}")

    return tb_df

def load_tb_records(conn, df):
    """Load TB data into database"""
    print("\n📊 Loading TB records into database...")

    cursor = conn.cursor()

    # Get TB disease ID
    cursor.execute("SELECT id FROM diseases WHERE code = 'TB'")
    result = cursor.fetchone()
    if not result:
        print("❌ Tuberculosis disease not found in database")
        return 0

    disease_id = result[0]

    # Get region mapping
    cursor.execute("SELECT code, id FROM regions")
    region_map = {row[0]: row[1] for row in cursor.fetchall()}

    # Prepare records - TB data is annual, so we use Jan 1st of each year as the date
    records = []
    skipped = 0

    for _, row in df.iterrows():
        region_id = region_map.get(row['iso_code'])
        if not region_id:
            skipped += 1
            continue

        # Use January 1st of the year as the date
        record_date = date(int(row['year']), 1, 1)

        records.append((
            disease_id,
            region_id,
            record_date,
            int(row['total_cases']),
            0,  # new_cases (annual data, so same as total for that year)
            int(row['total_deaths']),
            0,  # new_deaths
            round(row['incidence_rate'], 2),
            round(row['mortality_rate'], 2),
            'WHO_TB'
        ))

    print(f"   Preparing to insert {len(records):,} records...")
    print(f"   Skipped {skipped} records (no matching region)")

    # Clear existing WHO TB data
    cursor.execute("""
        DELETE FROM disease_records
        WHERE disease_id = %s AND data_source = 'WHO_TB'
    """, (disease_id,))
    print(f"   Cleared existing WHO TB data")

    # Bulk insert
    insert_query = """
        INSERT INTO disease_records
        (disease_id, region_id, date, total_cases, new_cases, total_deaths, new_deaths, incidence_rate, mortality_rate, data_source)
        VALUES %s
    """

    execute_values(cursor, insert_query, records)
    conn.commit()
    cursor.close()

    print(f"✅ Successfully loaded {len(records):,} TB records")
    return len(records)

def verify_tb_data(conn):
    """Verify TB data"""
    print("\n✅ Verifying TB data...")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*), COUNT(DISTINCT region_id), MIN(date), MAX(date)
        FROM disease_records
        WHERE data_source = 'WHO_TB'
    """)
    total, countries, min_date, max_date = cursor.fetchone()

    print(f"\n📈 TB Data Summary:")
    print(f"   Total records: {total:,}")
    print(f"   Countries: {countries}")
    print(f"   Year range: {min_date.year if min_date else 'N/A'} to {max_date.year if max_date else 'N/A'}")

    # Top TB burden countries (2022)
    cursor.execute("""
        SELECT r.name, dr.date, dr.total_cases, dr.total_deaths
        FROM disease_records dr
        JOIN regions r ON dr.region_id = r.id
        WHERE dr.data_source = 'WHO_TB' AND EXTRACT(YEAR FROM dr.date) = 2022
        ORDER BY dr.total_cases DESC
        LIMIT 5
    """)

    print(f"\n🔍 Top TB burden countries (2022):")
    for row in cursor.fetchall():
        print(f"   {row[0]}: Cases: {row[2]:,}, Deaths: {row[3]:,}")

    cursor.close()

def main():
    print("=" * 60)
    print("🫁 HealthMap Tuberculosis Data Ingestion Pipeline")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Download
    raw_df = download_who_tb_data()

    # Process
    clean_df = process_tb_data(raw_df)

    # Connect
    print("\n🔌 Connecting to database...")
    try:
        conn = get_db_connection()
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

    # Load
    records_loaded = load_tb_records(conn, clean_df)

    # Verify
    verify_tb_data(conn)

    conn.close()

    print("\n" + "=" * 60)
    print(f"✅ TB Ingestion completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()

-- Enable PostGIS extension for geospatial queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create tables
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20) UNIQUE,
    level VARCHAR(50),
    parent_id INTEGER REFERENCES regions(id),
    latitude FLOAT,
    longitude FLOAT,
    population BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS diseases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) UNIQUE,
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS disease_records (
    id SERIAL PRIMARY KEY,
    disease_id INTEGER NOT NULL REFERENCES diseases(id),
    region_id INTEGER NOT NULL REFERENCES regions(id),
    date DATE NOT NULL,
    total_cases BIGINT DEFAULT 0,
    new_cases INTEGER DEFAULT 0,
    total_deaths BIGINT DEFAULT 0,
    new_deaths INTEGER DEFAULT 0,
    incidence_rate FLOAT,
    mortality_rate FLOAT,
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS climate_records (
    id SERIAL PRIMARY KEY,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    date DATE NOT NULL,
    temp_avg FLOAT,
    temp_min FLOAT,
    temp_max FLOAT,
    rainfall FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    pressure FLOAT,
    data_source VARCHAR(100) DEFAULT 'OpenWeather',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS economic_records (
    id SERIAL PRIMARY KEY,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    year INTEGER NOT NULL,
    gdp_per_capita FLOAT,
    poverty_rate FLOAT,
    unemployment_rate FLOAT,
    urban_population_pct FLOAT,
    population_density FLOAT,
    hospital_beds_per_1000 FLOAT,
    doctors_per_1000 FLOAT,
    vaccination_rate FLOAT,
    data_source VARCHAR(100) DEFAULT 'WorldBank',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS data_ingestion_log (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    disease VARCHAR(100),
    records_inserted INTEGER,
    records_updated INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20),
    error_message TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_disease_records_disease_region ON disease_records(disease_id, region_id);
CREATE INDEX IF NOT EXISTS idx_disease_records_date ON disease_records(date);
CREATE INDEX IF NOT EXISTS idx_climate_records_region_date ON climate_records(region_id, date);
CREATE INDEX IF NOT EXISTS idx_regions_code ON regions(code);
CREATE INDEX IF NOT EXISTS idx_regions_level ON regions(level);

-- Seed initial diseases
INSERT INTO diseases (name, code, category, description) VALUES
('COVID-19', 'COVID19', 'infectious', 'Coronavirus disease caused by SARS-CoV-2'),
('Tuberculosis', 'TB', 'infectious', 'Bacterial infection primarily affecting lungs'),
('Malaria', 'MALARIA', 'infectious', 'Parasitic disease transmitted by mosquitoes')
ON CONFLICT (name) DO NOTHING;


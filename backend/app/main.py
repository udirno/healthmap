from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database import engine, get_db, Base
from app.api.routes import disease, correlations, insights, regions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    import app.models  # noqa: ensure models are registered
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Global Disease Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "HealthMap API",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/seed")
async def seed_database(db: Session = Depends(get_db)):
    """Seed the database with sample disease data. Safe to call multiple times."""
    import random
    from datetime import date, timedelta
    from app.models import Region, Disease, DiseaseRecord, ClimateRecord

    # Check if already seeded
    existing = db.query(Region).first()
    if existing:
        count = db.query(DiseaseRecord).count()
        return {"message": f"Database already seeded with {count} disease records"}

    # Seed regions
    regions_data = [
        ("United States", "USA", "country", 37.0902, -95.7129, 331000000),
        ("India", "IND", "country", 20.5937, 78.9629, 1380000000),
        ("Brazil", "BRA", "country", -14.2350, -51.9253, 212000000),
        ("United Kingdom", "GBR", "country", 55.3781, -3.4360, 67900000),
        ("Germany", "DEU", "country", 51.1657, 10.4515, 83200000),
        ("France", "FRA", "country", 46.2276, 2.2137, 65300000),
        ("Italy", "ITA", "country", 41.8719, 12.5674, 60500000),
        ("Spain", "ESP", "country", 40.4637, -3.7492, 46750000),
        ("Canada", "CAN", "country", 56.1304, -106.3468, 38000000),
        ("Japan", "JPN", "country", 36.2048, 138.2529, 126500000),
        ("South Korea", "KOR", "country", 35.9078, 127.7669, 51780000),
        ("Australia", "AUS", "country", -25.2744, 133.7751, 25690000),
        ("China", "CHN", "country", 35.8617, 104.1954, 1400000000),
        ("South Africa", "ZAF", "country", -30.5595, 22.9375, 59300000),
        ("Mexico", "MEX", "country", 23.6345, -102.5528, 128900000),
        ("Nigeria", "NGA", "country", 9.0820, 8.6753, 206000000),
        ("Indonesia", "IDN", "country", -0.7893, 113.9213, 273500000),
        ("Russia", "RUS", "country", 61.5240, 105.3188, 145900000),
        ("Turkey", "TUR", "country", 38.9637, 35.2433, 84300000),
        ("Argentina", "ARG", "country", -38.4161, -63.6167, 45380000),
    ]

    region_objs = {}
    for name, code, level, lat, lon, pop in regions_data:
        r = Region(name=name, code=code, level=level, latitude=lat, longitude=lon, population=pop)
        db.add(r)
        db.flush()
        region_objs[code] = r

    # Seed diseases
    diseases_data = [
        ("COVID-19", "COVID19", "infectious", "Coronavirus disease caused by SARS-CoV-2"),
        ("Tuberculosis", "TB", "infectious", "Bacterial infection primarily affecting lungs"),
        ("Malaria", "MALARIA", "infectious", "Parasitic disease transmitted by mosquitoes"),
    ]

    disease_objs = {}
    for name, code, cat, desc in diseases_data:
        d = Disease(name=name, code=code, category=cat, description=desc)
        db.add(d)
        db.flush()
        disease_objs[name] = d

    # Seed COVID-19 data: daily records for 2022
    random.seed(42)  # Reproducible
    start = date(2022, 1, 1)
    total_records = 0

    # Base case rates per country (approximate daily new cases at peak)
    base_rates = {
        "USA": 150000, "IND": 100000, "BRA": 50000, "GBR": 80000,
        "DEU": 60000, "FRA": 70000, "ITA": 40000, "ESP": 35000,
        "CAN": 20000, "JPN": 50000, "KOR": 30000, "AUS": 15000,
        "CHN": 5000, "ZAF": 10000, "MEX": 15000, "NGA": 2000,
        "IDN": 20000, "RUS": 40000, "TUR": 25000, "ARG": 20000,
    }

    covid = disease_objs["COVID-19"]
    for code, region in region_objs.items():
        base = base_rates.get(code, 10000)
        total_cases = 0
        total_deaths = 0

        for day_offset in range(365):
            d = start + timedelta(days=day_offset)
            # Simulate wave pattern: peak in Jan, dip in summer, rise in winter
            month_factor = 1.0
            m = d.month
            if m in (1, 2, 12):
                month_factor = 1.5
            elif m in (6, 7, 8):
                month_factor = 0.3
            elif m in (3, 4, 5):
                month_factor = 0.7
            else:
                month_factor = 0.9

            new_cases = max(0, int(base * month_factor * random.uniform(0.5, 1.5)))
            new_deaths = max(0, int(new_cases * random.uniform(0.005, 0.02)))
            total_cases += new_cases
            total_deaths += new_deaths

            pop = region.population or 1
            record = DiseaseRecord(
                disease_id=covid.id,
                region_id=region.id,
                date=d,
                new_cases=new_cases,
                new_deaths=new_deaths,
                total_cases=total_cases,
                total_deaths=total_deaths,
                incidence_rate=round((new_cases / pop) * 100000, 2),
                mortality_rate=round((total_deaths / total_cases) * 100, 2) if total_cases > 0 else 0,
                data_source="sample_data",
            )
            db.add(record)
            total_records += 1

    # Seed some climate data for correlation analysis
    for code, region in region_objs.items():
        base_temp = {"USA": 15, "IND": 28, "BRA": 25, "GBR": 10, "DEU": 9,
                     "FRA": 12, "ITA": 14, "ESP": 16, "CAN": 5, "JPN": 15,
                     "KOR": 12, "AUS": 22, "CHN": 14, "ZAF": 18, "MEX": 21,
                     "NGA": 27, "IDN": 27, "RUS": 5, "TUR": 13, "ARG": 16}.get(code, 15)

        for day_offset in range(365):
            d = start + timedelta(days=day_offset)
            seasonal = 10 * __import__('math').sin((d.timetuple().tm_yday - 80) / 365 * 2 * 3.14159)
            temp = base_temp + seasonal + random.uniform(-3, 3)

            cr = ClimateRecord(
                region_id=region.id,
                date=d,
                temp_avg=round(temp, 1),
                temp_min=round(temp - random.uniform(3, 8), 1),
                temp_max=round(temp + random.uniform(3, 8), 1),
                rainfall=round(random.uniform(0, 15), 1),
                humidity=round(random.uniform(30, 90), 1),
                wind_speed=round(random.uniform(2, 20), 1),
                pressure=round(random.uniform(1000, 1030), 1),
            )
            db.add(cr)

    db.commit()
    return {"message": f"Database seeded successfully with {total_records} disease records across {len(region_objs)} countries"}


# Include routers
app.include_router(disease.router, prefix="/api/diseases", tags=["diseases"])
app.include_router(correlations.router, prefix="/api/correlations", tags=["correlations"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(regions.router, prefix="/api/regions", tags=["regions"])

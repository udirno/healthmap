from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class EconomicRecord(Base):
    __tablename__ = "economic_records"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    year = Column(Integer, nullable=False, index=True)

    # Economic indicators
    gdp_per_capita = Column(Float)
    poverty_rate = Column(Float)
    unemployment_rate = Column(Float)

    # Demographics
    urban_population_pct = Column(Float)
    population_density = Column(Float)

    # Health infrastructure
    hospital_beds_per_1000 = Column(Float)
    doctors_per_1000 = Column(Float)
    vaccination_rate = Column(Float)

    # Metadata
    data_source = Column(String, default="WorldBank")
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    region = relationship("Region", back_populates="economic_records")

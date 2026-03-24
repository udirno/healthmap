from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    code = Column(String, unique=True)  # ICD codes or custom
    category = Column(String)  # 'infectious', 'chronic', etc.
    description = Column(String)

    # Relationships
    records = relationship("DiseaseRecord", back_populates="disease")

class DiseaseRecord(Base):
    __tablename__ = "disease_records"

    id = Column(Integer, primary_key=True, index=True)
    disease_id = Column(Integer, ForeignKey('diseases.id'), nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Metrics
    total_cases = Column(Integer, default=0)
    new_cases = Column(Integer, default=0)
    total_deaths = Column(Integer, default=0)
    new_deaths = Column(Integer, default=0)

    # Rates (per 100k population)
    incidence_rate = Column(Float)
    mortality_rate = Column(Float)

    # Metadata
    data_source = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    disease = relationship("Disease", back_populates="records")
    region = relationship("Region", back_populates="disease_records")

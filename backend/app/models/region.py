from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    code = Column(String, unique=True, index=True)
    level = Column(String)
    parent_id = Column(Integer, ForeignKey('regions.id'), nullable=True)

    latitude = Column(Float)
    longitude = Column(Float)
    population = Column(Float)

    parent = relationship("Region", remote_side=[id], backref="children")
    disease_records = relationship("DiseaseRecord", back_populates="region")
    climate_records = relationship("ClimateRecord", back_populates="region")
    economic_records = relationship("EconomicRecord", back_populates="region")

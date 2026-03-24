from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ClimateRecord(Base):
    __tablename__ = "climate_records"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    date = Column(Date, nullable=False, index=True)

    temp_avg = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)
    rainfall = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    pressure = Column(Float)

    data_source = Column(String, default="OpenWeather")
    created_at = Column(DateTime, server_default=func.now())

    region = relationship("Region", back_populates="climate_records")

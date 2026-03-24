from pydantic import BaseModel
from datetime import date
from typing import Optional

class DiseaseBase(BaseModel):
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

class DiseaseCreate(DiseaseBase):
    pass

class Disease(DiseaseBase):
    id: int

    class Config:
        from_attributes = True

class DiseaseRecordBase(BaseModel):
    disease_id: int
    region_id: int
    date: date
    total_cases: int = 0
    new_cases: int = 0
    total_deaths: int = 0
    new_deaths: int = 0
    incidence_rate: Optional[float] = None
    mortality_rate: Optional[float] = None

class DiseaseRecordCreate(DiseaseRecordBase):
    pass

class DiseaseRecord(DiseaseRecordBase):
    id: int
    data_source: Optional[str] = None

    class Config:
        from_attributes = True

class DiseaseDataResponse(BaseModel):
    disease: str
    region: str
    dates: list[date]
    total_cases: list[int]
    new_cases: list[int]
    total_deaths: list[int]
    new_deaths: list[int]

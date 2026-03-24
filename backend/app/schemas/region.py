from pydantic import BaseModel
from typing import Optional

class RegionBase(BaseModel):
    name: str
    code: str
    level: str
    parent_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None

class RegionCreate(RegionBase):
    pass

class Region(RegionBase):
    id: int

    class Config:
        from_attributes = True

class RegionHierarchy(Region):
    children: list['RegionHierarchy'] = []

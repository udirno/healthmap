from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.region import Region
from app.schemas.region import Region as RegionSchema

router = APIRouter()

@router.get("/", response_model=List[RegionSchema])
async def get_regions(
    level: Optional[str] = Query(None, description="Filter by level (world, country, state)"),
    parent_code: Optional[str] = Query(None, description="Get children of this region"),
    db: Session = Depends(get_db)
):
    """Get regions, optionally filtered by level or parent"""

    query = db.query(Region)

    if level:
        query = query.filter(Region.level == level)

    if parent_code:
        parent = db.query(Region).filter(Region.code == parent_code).first()
        if parent:
            query = query.filter(Region.parent_id == parent.id)

    return query.all()

@router.get("/search")
async def search_regions(
    q: str = Query(..., description="Search term"),
    db: Session = Depends(get_db)
):
    """Search regions by name"""

    regions = db.query(Region).filter(
        Region.name.ilike(f"%{q}%")
    ).limit(20).all()

    return regions

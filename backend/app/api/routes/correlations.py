from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.services import CorrelationService

router = APIRouter()

@router.get("/disease-climate")
async def get_disease_climate_correlation(
    disease: str = Query(..., description="Disease name"),
    region: str = Query(..., description="Region code"),
    climate_factor: str = Query("temp_avg", description="Climate factor (temp_avg, rainfall, humidity)"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Compute correlation between disease and climate factor"""

    result = CorrelationService.compute_disease_climate_correlation(
        db, disease, region, climate_factor, start_date, end_date
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result

@router.get("/all")
async def get_all_correlations(
    disease: str = Query(..., description="Disease name"),
    region: str = Query(..., description="Region code"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get all climate correlations for a disease"""

    results = CorrelationService.get_all_correlations(
        db, disease, region, start_date, end_date
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Insufficient data for correlation analysis"
        )

    return results

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from app.database import get_db
from app.services import DiseaseService, TrendService
from app.schemas.disease import Disease, DiseaseDataResponse

router = APIRouter()

@router.get("/", response_model=List[Disease])
async def get_diseases(db: Session = Depends(get_db)):
    """Get all available diseases"""
    return DiseaseService.get_diseases(db)

@router.get("/{disease_name}/data")
async def get_disease_data(
    disease_name: str,
    region_code: str = Query(..., description="Region code (e.g., 'USA', 'IND')"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get time-series disease data for a specific region"""

    data = DiseaseService.get_disease_data(
        db, disease_name, region_code, start_date, end_date
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for {disease_name} in {region_code}"
        )

    return data

@router.get("/{disease_name}/metrics")
async def get_disease_metrics(
    disease_name: str,
    region_code: str = Query(..., description="Region code"),
    db: Session = Depends(get_db)
):
    """Get latest disease metrics including trends"""

    metrics = DiseaseService.get_latest_metrics(db, disease_name, region_code)

    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"No metrics found for {disease_name} in {region_code}"
        )

    return metrics

@router.get("/{disease_name}/period-metrics")
async def get_period_metrics(
    disease_name: str,
    region_code: str = Query(..., description="Region code"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """Get aggregated disease metrics for a specific time period"""

    metrics = DiseaseService.get_metrics_for_period(
        db, disease_name, region_code, start_date, end_date
    )

    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for {disease_name} in {region_code} for the specified period"
        )

    return metrics

@router.get("/{disease_name}/time-series")
async def get_time_series(
    disease_name: str,
    region_code: str = Query(..., description="Region code"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """Get time-series data for charting (no AI call needed)"""

    data = TrendService.get_time_series_data(
        db, disease_name, region_code, str(start_date), str(end_date)
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No time series data for {disease_name} in {region_code}"
        )

    return data

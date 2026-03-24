from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.services import DiseaseService, CorrelationService, AIService, TrendService
from app.schemas.insights import InsightQuery, InsightResponse, Anomaly
from app.models import ClimateRecord, EconomicRecord, Region

router = APIRouter()

@router.post("/", response_model=InsightResponse)
async def generate_insight(
    query: InsightQuery,
    db: Session = Depends(get_db)
):
    """Generate AI-powered insight based on user question"""

    # Check if this is a multi-region comparison query
    is_comparison = query.regions and len(query.regions) > 1

    if is_comparison:
        # Handle multi-region comparison
        return await handle_region_comparison(query, db)

    # Gather relevant data based on query
    disease_data = None
    correlation_data = None
    climate_data = None
    economic_data = None

    if query.disease and query.region:
        # Get region object
        region = db.query(Region).filter(Region.code == query.region).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")

        # Use period metrics if date range provided, otherwise latest
        if query.start_date and query.end_date:
            disease_data = DiseaseService.get_metrics_for_period(
                db, query.disease, query.region, query.start_date, query.end_date
            )
        else:
            disease_data = DiseaseService.get_latest_metrics(
                db, query.disease, query.region
            )

        # Get correlations
        correlation_data = CorrelationService.get_all_correlations(
            db, query.disease, query.region
        )

        # Get climate data for the period
        if query.start_date and query.end_date:
            climate_records = db.query(ClimateRecord).filter(
                ClimateRecord.region_id == region.id,
                ClimateRecord.date >= query.start_date,
                ClimateRecord.date <= query.end_date
            ).all()

            if climate_records:
                climate_data = {
                    "avg_temperature": sum(r.temp_avg for r in climate_records if r.temp_avg) / len([r for r in climate_records if r.temp_avg]) if any(r.temp_avg for r in climate_records) else None,
                    "avg_rainfall": sum(r.rainfall for r in climate_records if r.rainfall) / len([r for r in climate_records if r.rainfall]) if any(r.rainfall for r in climate_records) else None,
                    "avg_humidity": sum(r.humidity for r in climate_records if r.humidity) / len([r for r in climate_records if r.humidity]) if any(r.humidity for r in climate_records) else None,
                    "period_start": query.start_date,
                    "period_end": query.end_date,
                    "num_records": len(climate_records)
                }

        # Get economic data (most recent year in range)
        if query.start_date:
            year = datetime.strptime(query.start_date, "%Y-%m-%d").year
            economic_record = db.query(EconomicRecord).filter(
                EconomicRecord.region_id == region.id,
                EconomicRecord.year <= year
            ).order_by(EconomicRecord.year.desc()).first()

            if economic_record:
                economic_data = {
                    "year": economic_record.year,
                    "gdp_per_capita": economic_record.gdp_per_capita,
                    "poverty_rate": economic_record.poverty_rate,
                    "unemployment_rate": economic_record.unemployment_rate,
                    "urban_population_pct": economic_record.urban_population_pct,
                    "hospital_beds_per_1000": economic_record.hospital_beds_per_1000,
                    "doctors_per_1000": economic_record.doctors_per_1000,
                    "vaccination_rate": economic_record.vaccination_rate
                }

    # Detect anomalies if we have date range
    anomaly_data = None
    time_series_data = None
    trend_analysis = None

    if query.start_date and query.end_date:
        # Detect anomalies
        anomaly_data = TrendService.detect_anomalies(
            db, query.disease, query.region, query.start_date, query.end_date
        )

        # Get time series for visualization
        time_series_data = TrendService.get_time_series_data(
            db, query.disease, query.region, query.start_date, query.end_date
        )

        # Calculate growth rate
        trend_analysis = TrendService.calculate_growth_rate(
            db, query.disease, query.region
        )

    # Convert conversation history to dict format for Claude
    conversation_history = None
    if query.conversation_history:
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in query.conversation_history
        ]

    # Generate insight using AI with full context (including anomalies)
    ai_service = AIService()
    narrative = ai_service.generate_insight(
        question=query.question,
        disease_data=disease_data,
        climate_data=climate_data,
        correlation_data=correlation_data,
        economic_data=economic_data,
        conversation_history=conversation_history
    )

    # Build response
    correlations = []
    if correlation_data:
        for corr in correlation_data:
            correlations.append({
                "factor1": query.disease,
                "factor2": corr["climate_factor"],
                "correlation_coefficient": corr["pearson_correlation"],
                "p_value": corr["pearson_p_value"],
                "interpretation": corr["interpretation"]
            })

    # Build anomalies list
    anomalies = []
    if anomaly_data and anomaly_data.get("anomalies"):
        for anom in anomaly_data["anomalies"]:
            anomalies.append(Anomaly(
                date=anom["date"],
                value=anom["value"],
                type=anom["type"],
                severity=anom["severity"],
                z_score=anom["z_score"],
                deviation_pct=anom["deviation_pct"]
            ))

    return InsightResponse(
        query=query.question,
        narrative=narrative,
        correlations=correlations,
        supporting_data={
            "disease_metrics": disease_data,
            "climate_data": climate_data,
            "economic_data": economic_data,
            "correlation_analysis": correlation_data
        },
        visualization_data={
            "time_series": time_series_data,
            "chart_type": "line" if time_series_data else None
        } if time_series_data else None,
        anomalies=anomalies,
        trend_data=trend_analysis
    )


async def handle_region_comparison(query: InsightQuery, db: Session) -> InsightResponse:
    """Handle multi-region comparison queries"""

    if not query.disease or not query.regions:
        raise HTTPException(status_code=400, detail="Disease and regions required for comparison")

    # Fetch data for all regions
    comparison_data = {}

    for region_code in query.regions:
        region = db.query(Region).filter(Region.code == region_code).first()
        if not region:
            continue

        # Get disease data for this region
        if query.start_date and query.end_date:
            region_disease_data = DiseaseService.get_metrics_for_period(
                db, query.disease, region_code, query.start_date, query.end_date
            )
        else:
            region_disease_data = DiseaseService.get_latest_metrics(
                db, query.disease, region_code
            )

        # Get correlations
        region_correlations = CorrelationService.get_all_correlations(
            db, query.disease, region_code
        )

        # Get climate data
        climate_data = None
        if query.start_date and query.end_date:
            climate_records = db.query(ClimateRecord).filter(
                ClimateRecord.region_id == region.id,
                ClimateRecord.date >= query.start_date,
                ClimateRecord.date <= query.end_date
            ).all()

            if climate_records:
                climate_data = {
                    "avg_temperature": sum(r.temp_avg for r in climate_records if r.temp_avg) / len([r for r in climate_records if r.temp_avg]) if any(r.temp_avg for r in climate_records) else None,
                    "avg_rainfall": sum(r.rainfall for r in climate_records if r.rainfall) / len([r for r in climate_records if r.rainfall]) if any(r.rainfall for r in climate_records) else None,
                }

        # Get economic data
        economic_data = None
        if query.start_date:
            year = datetime.strptime(query.start_date, "%Y-%m-%d").year
            economic_record = db.query(EconomicRecord).filter(
                EconomicRecord.region_id == region.id,
                EconomicRecord.year <= year
            ).order_by(EconomicRecord.year.desc()).first()

            if economic_record:
                economic_data = {
                    "gdp_per_capita": economic_record.gdp_per_capita,
                    "hospital_beds_per_1000": economic_record.hospital_beds_per_1000,
                    "vaccination_rate": economic_record.vaccination_rate
                }

        comparison_data[region.name] = {
            "disease_data": region_disease_data,
            "correlations": region_correlations,
            "climate_data": climate_data,
            "economic_data": economic_data
        }

    # Use the comparison insight function
    ai_service = AIService()
    narrative = ai_service.generate_comparison_insight(
        regions=[r for r in query.regions],
        disease=query.disease,
        comparison_data=comparison_data
    )

    return InsightResponse(
        query=query.question,
        narrative=narrative,
        correlations=[],
        supporting_data={
            "comparison_data": comparison_data
        }
    )

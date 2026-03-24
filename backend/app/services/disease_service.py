from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from typing import List, Optional
from app.models.disease import Disease, DiseaseRecord
from app.models.region import Region
from app.schemas.disease import DiseaseDataResponse

class DiseaseService:

    @staticmethod
    def get_diseases(db: Session) -> List[Disease]:
        """Get all available diseases"""
        return db.query(Disease).all()

    @staticmethod
    def get_disease_by_name(db: Session, name: str) -> Optional[Disease]:
        """Get disease by name"""
        return db.query(Disease).filter(Disease.name == name).first()

    @staticmethod
    def get_disease_data(
        db: Session,
        disease_name: str,
        region_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Optional[DiseaseDataResponse]:
        """Get time-series disease data for a region"""

        # Get disease and region
        disease = db.query(Disease).filter(Disease.name == disease_name).first()
        region = db.query(Region).filter(Region.code == region_code).first()

        if not disease or not region:
            return None

        # Build query
        query = db.query(DiseaseRecord).filter(
            and_(
                DiseaseRecord.disease_id == disease.id,
                DiseaseRecord.region_id == region.id
            )
        )

        # Add date filters
        if start_date:
            query = query.filter(DiseaseRecord.date >= start_date)
        if end_date:
            query = query.filter(DiseaseRecord.date <= end_date)

        # Order by date
        records = query.order_by(DiseaseRecord.date).all()

        if not records:
            return None

        # Format response
        return DiseaseDataResponse(
            disease=disease_name,
            region=region.name,
            dates=[r.date for r in records],
            total_cases=[r.total_cases for r in records],
            new_cases=[r.new_cases for r in records],
            total_deaths=[r.total_deaths for r in records],
            new_deaths=[r.new_deaths for r in records]
        )

    @staticmethod
    def get_latest_metrics(
        db: Session,
        disease_name: str,
        region_code: str
    ) -> Optional[dict]:
        """Get latest disease metrics for a region"""

        disease = db.query(Disease).filter(Disease.name == disease_name).first()
        region = db.query(Region).filter(Region.code == region_code).first()

        if not disease or not region:
            return None

        # Get latest record
        latest = db.query(DiseaseRecord).filter(
            and_(
                DiseaseRecord.disease_id == disease.id,
                DiseaseRecord.region_id == region.id
            )
        ).order_by(DiseaseRecord.date.desc()).first()

        if not latest:
            return None

        # Get 7-day and 14-day averages
        seven_days_ago = latest.date - timedelta(days=7)
        fourteen_days_ago = latest.date - timedelta(days=14)

        avg_7day = db.query(func.avg(DiseaseRecord.new_cases)).filter(
            and_(
                DiseaseRecord.disease_id == disease.id,
                DiseaseRecord.region_id == region.id,
                DiseaseRecord.date >= seven_days_ago,
                DiseaseRecord.date <= latest.date
            )
        ).scalar() or 0
        avg_7day = float(avg_7day)

        avg_14day = db.query(func.avg(DiseaseRecord.new_cases)).filter(
            and_(
                DiseaseRecord.disease_id == disease.id,
                DiseaseRecord.region_id == region.id,
                DiseaseRecord.date >= fourteen_days_ago,
                DiseaseRecord.date <= latest.date
            )
        ).scalar() or 0
        avg_14day = float(avg_14day)

        # Determine trend
        if avg_7day > avg_14day * 1.1:
            trend = "increasing"
        elif avg_7day < avg_14day * 0.9:
            trend = "declining"
        else:
            trend = "stable"

        # Calculate case fatality rate (deaths as % of cases)
        cfr = (latest.total_deaths / latest.total_cases * 100) if latest.total_cases > 0 else 0.0

        return {
            "disease": disease_name,
            "region": region.name,
            "date": latest.date,
            "total_cases": latest.total_cases,
            "new_cases": latest.new_cases,
            "total_deaths": latest.total_deaths,
            "new_deaths": latest.new_deaths,
            "avg_7day": round(avg_7day, 2),
            "avg_14day": round(avg_14day, 2),
            "trend": trend,
            "incidence_rate": latest.incidence_rate,
            "mortality_rate": round(cfr, 1)
        }

    @staticmethod
    def get_metrics_for_period(
        db: Session,
        disease_name: str,
        region_code: str,
        start_date: date,
        end_date: date
    ) -> Optional[dict]:
        """Get aggregated disease metrics for a specific date range"""

        disease = db.query(Disease).filter(Disease.name == disease_name).first()
        region = db.query(Region).filter(Region.code == region_code).first()

        if not disease or not region:
            return None

        # Get records in date range
        records = db.query(DiseaseRecord).filter(
            and_(
                DiseaseRecord.disease_id == disease.id,
                DiseaseRecord.region_id == region.id,
                DiseaseRecord.date >= start_date,
                DiseaseRecord.date <= end_date
            )
        ).order_by(DiseaseRecord.date).all()

        if not records:
            return None

        # Calculate aggregated metrics for the period
        total_new_cases = sum(r.new_cases for r in records)
        total_new_deaths = sum(r.new_deaths for r in records)

        # Get first and last record for the period
        first_record = records[0]
        last_record = records[-1]

        # Cases at start vs end of period
        cases_at_start = first_record.total_cases - first_record.new_cases
        cases_at_end = last_record.total_cases

        deaths_at_start = first_record.total_deaths - first_record.new_deaths
        deaths_at_end = last_record.total_deaths

        # Average daily new cases
        num_days = len(records)
        avg_daily_cases = total_new_cases / num_days if num_days > 0 else 0
        avg_daily_deaths = total_new_deaths / num_days if num_days > 0 else 0

        # Determine trend (compare first half to second half)
        if num_days >= 14:
            mid = num_days // 2
            first_half_avg = sum(r.new_cases for r in records[:mid]) / mid
            second_half_avg = sum(r.new_cases for r in records[mid:]) / (num_days - mid)

            if second_half_avg > first_half_avg * 1.1:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # Calculate case fatality rate (deaths as % of cases)
        cfr = (total_new_deaths / total_new_cases * 100) if total_new_cases > 0 else 0.0

        return {
            "disease": disease_name,
            "region": region.name,
            "period_start": start_date,
            "period_end": end_date,
            "total_new_cases": total_new_cases,
            "total_new_deaths": total_new_deaths,
            "cases_at_start": cases_at_start,
            "cases_at_end": cases_at_end,
            "deaths_at_start": deaths_at_start,
            "deaths_at_end": deaths_at_end,
            "avg_daily_cases": round(avg_daily_cases, 2),
            "avg_daily_deaths": round(avg_daily_deaths, 2),
            "num_days": num_days,
            "trend": trend,
            "incidence_rate": last_record.incidence_rate,
            "mortality_rate": round(cfr, 1)
        }

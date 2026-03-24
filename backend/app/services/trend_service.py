from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import math
from datetime import datetime, timedelta
from app.models import DiseaseRecord, Region


class TrendService:

    @staticmethod
    def detect_anomalies(
        db: Session,
        disease: str,
        region_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """Detect anomalies in disease data using statistical methods"""

        # Get region
        region = db.query(Region).filter(Region.code == region_code).first()
        if not region:
            return {"anomalies": [], "method": "none"}

        # Build query
        query = db.query(DiseaseRecord).join(Region).filter(
            Region.code == region_code,
            DiseaseRecord.new_cases.isnot(None)
        )

        if start_date and end_date:
            query = query.filter(
                DiseaseRecord.date >= start_date,
                DiseaseRecord.date <= end_date
            )

        # Get records ordered by date
        records = query.order_by(DiseaseRecord.date).all()

        if len(records) < 10:
            return {"anomalies": [], "method": "insufficient_data"}

        # Extract new cases
        cases = [float(r.new_cases) for r in records]
        dates = [r.date.strftime("%Y-%m-%d") for r in records]

        # Calculate statistics
        n = len(cases)
        mean = sum(cases) / n
        variance = sum((x - mean) ** 2 for x in cases) / n
        std = math.sqrt(variance)

        # Z-score method: flag values > 2.5 standard deviations
        anomaly_threshold = 2.5

        # Detect anomalies
        anomalies = []
        for i, (case_count, date_str) in enumerate(zip(cases, dates)):
            z_score = abs((case_count - mean) / (std + 1e-10))
            if z_score > anomaly_threshold:
                # Determine if spike or drop
                anomaly_type = "spike" if case_count > mean else "drop"

                # Calculate severity
                severity = "high" if z_score > 3.5 else "medium"

                anomalies.append({
                    "date": date_str,
                    "value": int(case_count),
                    "expected_range": f"{int(mean - std)}-{int(mean + std)}",
                    "z_score": round(z_score, 2),
                    "type": anomaly_type,
                    "severity": severity,
                    "deviation_pct": round(((case_count - mean) / mean) * 100, 1) if mean != 0 else 0
                })

        return {
            "anomalies": anomalies,
            "method": "z_score",
            "threshold": anomaly_threshold,
            "baseline_mean": int(mean),
            "baseline_std": int(std),
            "total_days_analyzed": len(records)
        }

    @staticmethod
    def get_time_series_data(
        db: Session,
        disease: str,
        region_code: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get time series data for visualization"""

        region = db.query(Region).filter(Region.code == region_code).first()
        if not region:
            return []

        records = db.query(DiseaseRecord).join(Region).filter(
            Region.code == region_code,
            DiseaseRecord.date >= start_date,
            DiseaseRecord.date <= end_date
        ).order_by(DiseaseRecord.date).all()

        return [
            {
                "date": r.date.strftime("%Y-%m-%d"),
                "new_cases": r.new_cases or 0,
                "new_deaths": r.new_deaths or 0,
                "total_cases": r.total_cases or 0,
                "total_deaths": r.total_deaths or 0
            }
            for r in records
        ]

    @staticmethod
    def calculate_growth_rate(
        db: Session,
        disease: str,
        region_code: str,
        window_days: int = 7
    ) -> Dict[str, Any]:
        """Calculate rolling growth rate"""

        region = db.query(Region).filter(Region.code == region_code).first()
        if not region:
            return {}

        # Get last 30 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        records = db.query(DiseaseRecord).join(Region).filter(
            Region.code == region_code,
            DiseaseRecord.date >= start_date,
            DiseaseRecord.date <= end_date
        ).order_by(DiseaseRecord.date).all()

        if len(records) < window_days * 2:
            return {}

        cases = [r.new_cases or 0 for r in records]

        # Calculate 7-day moving average
        moving_avg = []
        for i in range(len(cases) - window_days + 1):
            window = cases[i:i + window_days]
            avg = sum(window) / len(window)
            moving_avg.append(avg)

        # Calculate growth rate (current vs previous week)
        if len(moving_avg) >= 2:
            recent_avg = moving_avg[-1]
            previous_avg = moving_avg[-8] if len(moving_avg) >= 8 else moving_avg[0]

            if previous_avg > 0:
                growth_rate = ((recent_avg - previous_avg) / previous_avg) * 100
            else:
                growth_rate = 0

            return {
                "growth_rate_pct": round(growth_rate, 1),
                "current_7day_avg": round(recent_avg, 1),
                "previous_7day_avg": round(previous_avg, 1),
                "trend": "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable"
            }

        return {}

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from typing import List, Dict, Any
import math
from app.models.disease import DiseaseRecord, Disease
from app.models.climate import ClimateRecord
from app.models.region import Region


def _pearson(x: List[float], y: List[float]):
    """Pure-Python Pearson correlation coefficient and two-tailed p-value."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

    if std_x == 0 or std_y == 0:
        return 0.0, 1.0

    r = cov / (std_x * std_y)
    # Approximate p-value using t-distribution
    t_stat = r * math.sqrt((n - 2) / (1 - r * r + 1e-10))
    # Rough two-tailed p from t (good enough for display purposes)
    p = 2.0 * (1.0 / (1.0 + abs(t_stat)))  # simplified approximation
    return round(r, 4), round(p, 4)


def _spearman(x: List[float], y: List[float]):
    """Pure-Python Spearman rank correlation."""
    def _rank(data):
        sorted_indices = sorted(range(len(data)), key=lambda i: data[i])
        ranks = [0.0] * len(data)
        for rank_val, idx in enumerate(sorted_indices, 1):
            ranks[idx] = float(rank_val)
        return ranks

    rank_x = _rank(x)
    rank_y = _rank(y)
    return _pearson(rank_x, rank_y)


class CorrelationService:

    @staticmethod
    def compute_disease_climate_correlation(
        db: Session,
        disease_name: str,
        region_code: str,
        climate_factor: str = "temp_avg",
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """Compute correlation between disease cases and climate factors"""

        # Get disease and region
        disease = db.query(Disease).filter(Disease.name == disease_name).first()
        region = db.query(Region).filter(Region.code == region_code).first()

        if not disease or not region:
            return {"error": "Disease or region not found"}

        # Get disease records
        disease_query = db.query(DiseaseRecord).filter(
            and_(
                DiseaseRecord.disease_id == disease.id,
                DiseaseRecord.region_id == region.id
            )
        )

        if start_date:
            disease_query = disease_query.filter(DiseaseRecord.date >= start_date)
        if end_date:
            disease_query = disease_query.filter(DiseaseRecord.date <= end_date)

        disease_records = disease_query.all()

        # Get climate records
        climate_query = db.query(ClimateRecord).filter(
            ClimateRecord.region_id == region.id
        )

        if start_date:
            climate_query = climate_query.filter(ClimateRecord.date >= start_date)
        if end_date:
            climate_query = climate_query.filter(ClimateRecord.date <= end_date)

        climate_records = climate_query.all()

        if not disease_records or not climate_records:
            return {"error": "Insufficient data"}

        # Build date-keyed lookups and merge on date
        disease_by_date = {r.date: r.new_cases for r in disease_records}
        climate_by_date = {r.date: getattr(r, climate_factor) for r in climate_records}

        common_dates = sorted(set(disease_by_date) & set(climate_by_date))

        if len(common_dates) < 10:
            return {"error": "Insufficient overlapping data"}

        cases = [float(disease_by_date[d]) for d in common_dates]
        climate_vals = [float(climate_by_date[d]) for d in common_dates]

        # Compute correlations
        pearson_corr, pearson_p = _pearson(cases, climate_vals)
        spearman_corr, spearman_p = _spearman(cases, climate_vals)

        # Interpretation
        abs_corr = abs(pearson_corr)
        if abs_corr < 0.3:
            strength = "weak"
        elif abs_corr < 0.7:
            strength = "moderate"
        else:
            strength = "strong"

        direction = "positive" if pearson_corr > 0 else "negative"

        return {
            "disease": disease_name,
            "region": region.name,
            "climate_factor": climate_factor,
            "pearson_correlation": pearson_corr,
            "pearson_p_value": pearson_p,
            "spearman_correlation": spearman_corr,
            "spearman_p_value": spearman_p,
            "strength": strength,
            "direction": direction,
            "sample_size": len(common_dates),
            "interpretation": f"There is a {strength} {direction} correlation between {climate_factor} and {disease_name} cases."
        }

    @staticmethod
    def get_all_correlations(
        db: Session,
        disease_name: str,
        region_code: str,
        start_date: date = None,
        end_date: date = None
    ) -> List[Dict[str, Any]]:
        """Compute all climate correlations for a disease"""

        climate_factors = ["temp_avg", "rainfall", "humidity"]
        results = []

        for factor in climate_factors:
            result = CorrelationService.compute_disease_climate_correlation(
                db, disease_name, region_code, factor, start_date, end_date
            )
            if "error" not in result:
                results.append(result)

        return results

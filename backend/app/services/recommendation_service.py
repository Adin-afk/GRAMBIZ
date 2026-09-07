from sqlalchemy.orm import Session

from app.gis import service as gis_service
from app.models.business import (
    Business,
    BusinessCategory,
    BusinessCostTemplate,
    BusinessRevenueAssumption,
    InfrastructureStatistics,
    Market,
)
from app.models.geography import Village
from app.services import scoring_service


def _category_investment_range(db: Session, category_id: str) -> tuple[float | None, float | None]:
    templates = (
        db.query(BusinessCostTemplate)
        .filter(BusinessCostTemplate.category_id == category_id, BusinessCostTemplate.cost_type == "CAPITAL")
        .all()
    )
    if not templates:
        cat = db.get(BusinessCategory, category_id)
        return (cat.typical_min_investment if cat else None, cat.typical_max_investment if cat else None)
    total = sum(t.estimated_cost for t in templates)
    return (total * 0.85, total * 1.15)


def evaluate_category_for_village(db: Session, village: Village, category: BusinessCategory, available_capital: float) -> dict:
    count_5km = gis_service.get_competitor_count(db, village.latitude, village.longitude, 5.0, category.id)
    count_10km = gis_service.get_competitor_count(db, village.latitude, village.longitude, 10.0, category.id)

    markets_5km = gis_service.get_nearby_markets(db, village.latitude, village.longitude, 5.0)

    infra = (
        db.query(InfrastructureStatistics)
        .filter(InfrastructureStatistics.village_id == village.id)
        .first()
    )
    road_access = infra.road_access if infra else None

    revenue_assumption = (
        db.query(BusinessRevenueAssumption)
        .filter(BusinessRevenueAssumption.category_id == category.id)
        .first()
    )
    expected_margin_pct = revenue_assumption.expected_margin_pct if revenue_assumption else None
    seasonality_raw = revenue_assumption.seasonality_score if revenue_assumption else None

    min_inv, max_inv = _category_investment_range(db, category.id)

    # Nearest market distance among the 5km set, else None (unknown)
    market_distance_km = min((m["distance_km"] for m in markets_5km), default=None)

    components = {
        "demand": scoring_service.score_demand(village.population, village.households),
        "competition": scoring_service.score_competition(count_5km),
        "accessibility": scoring_service.score_accessibility(road_access, market_distance_km),
        "cost": scoring_service.score_cost(min_inv, available_capital),
        "margin": scoring_service.score_margin(expected_margin_pct),
        "market_access": scoring_service.score_market_access(len(markets_5km)),
        "seasonality": scoring_service.score_seasonality(seasonality_raw),
    }

    score_result = scoring_service.compute_opportunity_score(db, components)

    return {
        "category_id": category.id,
        "category_name": category.name,
        "opportunity_score": score_result["opportunity_score"],
        "components": score_result["components"],
        "weights_used": score_result["weights_used"],
        "competitor_count_5km": count_5km,
        "competitor_count_10km": count_10km,
        "competitor_density": gis_service.competitor_density(count_5km, count_10km),
        "market_count_5km": len(markets_5km),
        "estimated_investment_low": min_inv,
        "estimated_investment_high": max_inv,
    }


def recommend_businesses(db: Session, village: Village, available_capital: float) -> list[dict]:
    categories = db.query(BusinessCategory).filter(BusinessCategory.active.is_(True)).all()
    results = [evaluate_category_for_village(db, village, cat, available_capital) for cat in categories]
    results.sort(key=lambda r: r["opportunity_score"], reverse=True)
    return results

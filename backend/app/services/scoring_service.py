"""
Deterministic business-opportunity scoring.

Weights are read from ScoringWeightConfig (DB-editable via admin API), never
hard-coded in the frontend or here. This module contains no LLM calls - the
LLM (see app/ai) only *explains* these numbers after the fact, it never
computes them.
"""
from sqlalchemy.orm import Session

from app.models.config import ScoringWeightConfig


def get_active_weights(db: Session) -> ScoringWeightConfig:
    cfg = (
        db.query(ScoringWeightConfig)
        .filter(ScoringWeightConfig.active.is_(True))
        .order_by(ScoringWeightConfig.created_at.desc())
        .first()
    )
    if cfg is None:
        raise ValueError("No active scoring weight configuration found.")
    return cfg


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def score_demand(population: int | None, households: int | None) -> float:
    """Simple normalized demand proxy from population/household scale.
    Thresholds are conservative and documented, not fabricated precision."""
    if not population:
        return 0.3  # unknown population -> low-moderate default, not zero
    # Normalize against a 5,000-population reference typical of a large
    # Solapur rural village; villages above that cap at 1.0.
    return round(_clamp01(population / 5000), 3)


def score_competition(competitor_count_5km: int) -> float:
    """More competitors nearby -> lower score. 0 competitors = 1.0, 10+ = 0.0."""
    return round(_clamp01(1 - (competitor_count_5km / 10)), 3)


def score_accessibility(road_access: bool | None, market_distance_km: float | None) -> float:
    road_component = 0.5 if road_access else 0.0
    if market_distance_km is None:
        distance_component = 0.25
    else:
        # Closer market = better accessibility; 0km -> 0.5, 20km+ -> 0
        distance_component = _clamp01(0.5 - (market_distance_km / 40))
    return round(_clamp01(road_component + distance_component), 3)


def score_cost(initial_investment: float | None, available_capital: float) -> float:
    if not initial_investment or initial_investment <= 0:
        return 0.5
    ratio = available_capital / initial_investment
    return round(_clamp01(ratio), 3)


def score_margin(expected_margin_pct: float | None) -> float:
    if expected_margin_pct is None:
        return 0.4
    # 0% margin -> 0.0 ; 50%+ margin -> 1.0
    return round(_clamp01(expected_margin_pct / 50), 3)


def score_market_access(market_count_5km: int) -> float:
    return round(_clamp01(market_count_5km / 3), 3)


def score_seasonality(seasonality_score_raw: float | None) -> float:
    """seasonality_score_raw: 0 (steady demand) - 1 (highly seasonal).
    We invert it: less seasonal = higher opportunity score."""
    if seasonality_score_raw is None:
        return 0.5
    return round(_clamp01(1 - seasonality_score_raw), 3)


def compute_opportunity_score(db: Session, components: dict) -> dict:
    """
    components: dict with keys matching the score_* function outputs:
        demand, competition, accessibility, cost, margin, market_access, seasonality
    Returns the weighted composite (0-100 scale) plus each component.
    """
    weights = get_active_weights(db)
    weight_map = {
        "demand": weights.demand_weight,
        "competition": weights.competition_weight,
        "accessibility": weights.accessibility_weight,
        "cost": weights.cost_weight,
        "margin": weights.margin_weight,
        "market_access": weights.market_access_weight,
        "seasonality": weights.seasonality_weight,
    }
    total_weight = sum(weight_map.values())
    composite = 0.0
    for key, weight in weight_map.items():
        composite += components.get(key, 0.0) * weight
    if total_weight > 0:
        composite = composite / total_weight

    return {
        "opportunity_score": round(composite * 100, 1),
        "components": components,
        "weights_used": weight_map,
    }

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import scoring_service


def test_score_demand_no_population_returns_moderate_default():
    assert scoring_service.score_demand(None, None) == 0.3


def test_score_demand_scales_with_population():
    low = scoring_service.score_demand(500, 100)
    high = scoring_service.score_demand(5000, 1000)
    assert high > low
    assert high == 1.0  # capped at reference population


def test_score_competition_inverse_relationship():
    no_competitors = scoring_service.score_competition(0)
    many_competitors = scoring_service.score_competition(10)
    assert no_competitors == 1.0
    assert many_competitors == 0.0


def test_score_cost_ratio():
    assert scoring_service.score_cost(100000, 100000) == 1.0
    assert scoring_service.score_cost(200000, 100000) == 0.5
    assert scoring_service.score_cost(None, 100000) == 0.5


def test_score_margin_scaling():
    assert scoring_service.score_margin(None) == 0.4
    assert scoring_service.score_margin(0) == 0.0
    assert scoring_service.score_margin(50) == 1.0


def test_all_component_scores_within_bounds():
    """Every scoring function must return a value in [0, 1]."""
    checks = [
        scoring_service.score_demand(3000, 700),
        scoring_service.score_competition(3),
        scoring_service.score_accessibility(True, 5.0),
        scoring_service.score_cost(80000, 100000),
        scoring_service.score_margin(25),
        scoring_service.score_market_access(2),
        scoring_service.score_seasonality(0.4),
    ]
    for value in checks:
        assert 0.0 <= value <= 1.0

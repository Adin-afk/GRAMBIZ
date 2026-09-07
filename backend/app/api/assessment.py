from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai import gemini_service
from app.auth.dependencies import get_current_user, get_optional_current_user
from app.config import get_settings
from app.database.session import get_db
from app.financial import engine as fin_engine
from app.gis import service as gis_service
from app.models.assessment import BusinessAssessment
from app.models.business import BusinessCategory
from app.models.geography import Village
from app.models.users import User
from app.schemas.assessment import (
    AssessmentCreateRequest,
    AssessmentOut,
    RecommendationItem,
    RecommendRequest,
    RecommendResponse,
)
from app.services import recommendation_service

router = APIRouter(prefix="/api", tags=["business-analysis"])
settings = get_settings()


def _require_rural_village(db: Session, village_id: str) -> Village:
    village = db.get(Village, village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error_code": "LOCATION_NOT_FOUND", "message": "The selected village could not be found."},
        )
    return village


@router.post("/business/recommend", response_model=RecommendResponse)
def recommend_business(payload: RecommendRequest, db: Session = Depends(get_db)):
    """'What business should I start?' - evaluates every supported category
    for the given village/capital using the real deterministic scoring +
    PostGIS competitor/market data. Numbers are never invented client-side."""
    village = _require_rural_village(db, payload.village_id)

    if village.area_type != "RURAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error_code": "NOT_RURAL_SCOPE",
                "message": "This platform's primary model targets rural Solapur villages. "
                "This location is classified as non-rural.",
            },
        )

    results = recommendation_service.recommend_businesses(db, village, payload.available_capital)

    demo_note = (
        "Scores are computed from DEMO data (data_status=DEMO) since verified real-world "
        "Solapur statistics have not yet been imported for this village."
        if settings.DEMO_MODE
        else ""
    )

    return RecommendResponse(
        village_id=village.id,
        available_capital=payload.available_capital,
        recommendations=[
            RecommendationItem(
                category_id=r["category_id"],
                category_name=r["category_name"],
                opportunity_score=r["opportunity_score"],
                components=r["components"],
                competitor_count_5km=r["competitor_count_5km"],
                competitor_count_10km=r["competitor_count_10km"],
                estimated_investment_low=r["estimated_investment_low"],
                estimated_investment_high=r["estimated_investment_high"],
            )
            for r in results
        ],
        dataset_note=demo_note,
    )


@router.post("/assessment/create", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Full end-to-end analysis: location -> GIS -> competitor/market analysis
    -> deterministic scoring -> financial engine -> scheme match -> save."""
    village = _require_rural_village(db, payload.village_id)
    category = db.get(BusinessCategory, payload.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error_code": "CATEGORY_NOT_FOUND", "message": "The selected business category could not be found."},
        )

    eval_result = recommendation_service.evaluate_category_for_village(db, village, category, payload.available_capital)

    competitors_5km = gis_service.get_nearby_businesses(db, village.latitude, village.longitude, 5.0, category.id)
    competitors_10km = gis_service.get_nearby_businesses(db, village.latitude, village.longitude, 10.0, category.id)
    markets_10km = gis_service.get_nearby_markets(db, village.latitude, village.longitude, 10.0)

    # Financial feasibility (deterministic; no LLM)
    try:
        fin_base = fin_engine.compute_project_cost_and_loan(available_margin=payload.available_capital, db=db)
        matched_schemes = fin_engine.find_matching_schemes(db, fin_base["project_cost"])
    except fin_engine.FinancialValidationError as e:
        fin_base = {"error": str(e)}
        matched_schemes = []

    risk_level = "LOW" if eval_result["opportunity_score"] >= 70 else "MEDIUM" if eval_result["opportunity_score"] >= 45 else "HIGH"

    # Optional Gemini 2.5 Flash explanation layer: turns the deterministic
    # numbers above into a SWOT analysis + plain-language summary. Best-effort
    # only - never raises, and the assessment is saved either way. The
    # configuration check lives inside gemini_service (single source of
    # truth) rather than being duplicated here, so this always reflects the
    # same "configured" status the /api/health/services endpoint reports.
    ai_result = gemini_service.generate_assessment_explanation(
        {
            "village_name": village.village_name,
            "category_name": category.name,
            "available_capital": payload.available_capital,
            "opportunity_score": eval_result["opportunity_score"],
            "score_components": eval_result["components"],
            "competitor_count_5km": eval_result["competitor_count_5km"],
            "competitor_count_10km": eval_result["competitor_count_10km"],
            "market_count_5km": eval_result["market_count_5km"],
            "estimated_investment_low": eval_result["estimated_investment_low"],
            "estimated_investment_high": eval_result["estimated_investment_high"],
            "financial_analysis": fin_base,
            "matched_schemes": [s.scheme_name for s in matched_schemes],
            "risk_level": risk_level,
        }
    )

    assessment = BusinessAssessment(
        user_id=current_user.id if current_user else None,
        village_id=village.id,
        category_id=category.id,
        available_capital=payload.available_capital,
        opportunity_score=eval_result["opportunity_score"],
        demand_score=eval_result["components"]["demand"],
        competition_score=eval_result["components"]["competition"],
        accessibility_score=eval_result["components"]["accessibility"],
        margin_score=eval_result["components"]["margin"],
        market_access_score=eval_result["components"]["market_access"],
        seasonality_score=eval_result["components"]["seasonality"],
        market_analysis={"nearby_markets_10km": markets_10km},
        competitor_analysis={
            "competitors_5km": competitors_5km,
            "competitors_10km": competitors_10km,
            "competitor_count_5km": eval_result["competitor_count_5km"],
            "competitor_count_10km": eval_result["competitor_count_10km"],
            "density": eval_result["competitor_density"],
        },
        financial_analysis=fin_base,
        scheme_match={"matched_schemes": [s.scheme_name for s in matched_schemes], "count": len(matched_schemes)},
        risk_assessment={"risk_level": risk_level, "opportunity_score": eval_result["opportunity_score"]},
        swot=ai_result["swot"] if ai_result else None,
        ai_explanation=ai_result["ai_explanation"] if ai_result else None,
        dataset_version="solapur_rural_demo_v1" if settings.DEMO_MODE else None,
        model_version=settings.GEMINI_MODEL if ai_result else None,
        confidence_level="LOW" if settings.DEMO_MODE else "MEDIUM",
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/assessment/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    assessment = db.get(BusinessAssessment, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error_code": "ASSESSMENT_NOT_FOUND", "message": "The requested assessment could not be found."},
        )
    return assessment

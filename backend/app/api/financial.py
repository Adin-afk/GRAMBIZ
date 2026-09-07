from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.financial import engine as fin_engine
from app.models.schemes import LoanScheme
from app.schemas.financial import (
    FinancialCalculateRequest,
    FinancialCalculateResponse,
    RepaymentRequest,
    RepaymentResponse,
    SchemeOut,
)

router = APIRouter(prefix="/api", tags=["financial"])


def _scheme_to_dict(s: LoanScheme) -> dict:
    return {
        "id": s.id,
        "scheme_name": s.scheme_name,
        "provider": s.provider,
        "interest_rate": s.interest_rate,
        "tenure_years": s.tenure_years,
        "moratorium_months": s.moratorium_months,
        "maximum_loan": s.maximum_loan,
        "loan_percentage": s.loan_percentage,
        "beneficiary_contribution": s.beneficiary_contribution,
        "data_status": s.data_status,
        "source": s.source,
        "source_url": s.source_url,
    }


@router.post("/financial/calculate", response_model=FinancialCalculateResponse)
def calculate_financials(payload: FinancialCalculateRequest, db: Session = Depends(get_db)):
    try:
        base = fin_engine.compute_project_cost_and_loan(
            available_margin=payload.available_margin,
            beneficiary_contribution_pct=payload.beneficiary_contribution_pct,
            db=db,
        )
    except fin_engine.FinancialValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error_code": "INVALID_FINANCIAL_INPUT", "message": str(e)},
        )

    matched = fin_engine.find_matching_schemes(db, base["project_cost"])
    matched_dicts = [_scheme_to_dict(s) for s in matched]

    selected = None
    if payload.scheme_id:
        selected_scheme = next((s for s in matched if s.id == payload.scheme_id), None)
        if selected_scheme:
            selected = _scheme_to_dict(selected_scheme)
    elif matched:
        selected = _scheme_to_dict(matched[0])

    return FinancialCalculateResponse(
        available_margin=base["available_margin"],
        project_cost=base["project_cost"],
        loan_amount=base["loan_amount"],
        beneficiary_contribution_pct=base["beneficiary_contribution_pct"],
        matched_schemes=matched_dicts,
        selected_scheme=selected,
    )


@router.post("/financial/repayment", response_model=RepaymentResponse)
def repayment_schedule(payload: RepaymentRequest):
    try:
        result = fin_engine.build_repayment_schedule(
            principal=payload.principal,
            annual_interest_rate_pct=payload.annual_interest_rate_pct,
            tenure_years=payload.tenure_years,
            moratorium_months=payload.moratorium_months,
        )
    except fin_engine.FinancialValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error_code": "INVALID_FINANCIAL_INPUT", "message": str(e)},
        )
    return result


@router.get("/schemes", response_model=list[SchemeOut])
def list_schemes(db: Session = Depends(get_db)):
    schemes = db.query(LoanScheme).order_by(LoanScheme.scheme_name).all()
    return [
        SchemeOut(
            id=s.id,
            scheme_name=s.scheme_name,
            provider=s.provider,
            minimum_project_cost=s.minimum_project_cost,
            maximum_project_cost=s.maximum_project_cost,
            loan_percentage=s.loan_percentage,
            beneficiary_contribution=s.beneficiary_contribution,
            maximum_loan=s.maximum_loan,
            interest_rate=s.interest_rate,
            tenure_years=s.tenure_years,
            moratorium_months=s.moratorium_months,
            repayment_frequency=s.repayment_frequency,
            eligibility=s.eligibility,
            source=s.source,
            source_url=s.source_url,
            last_verified_date=s.last_verified_date.isoformat() if s.last_verified_date else None,
            data_status=s.data_status,
        )
        for s in schemes
    ]


@router.post("/schemes/match", response_model=list[SchemeOut])
def match_schemes(project_cost: float, db: Session = Depends(get_db)):
    matched = fin_engine.find_matching_schemes(db, project_cost)
    return [
        SchemeOut(
            id=s.id,
            scheme_name=s.scheme_name,
            provider=s.provider,
            minimum_project_cost=s.minimum_project_cost,
            maximum_project_cost=s.maximum_project_cost,
            loan_percentage=s.loan_percentage,
            beneficiary_contribution=s.beneficiary_contribution,
            maximum_loan=s.maximum_loan,
            interest_rate=s.interest_rate,
            tenure_years=s.tenure_years,
            moratorium_months=s.moratorium_months,
            repayment_frequency=s.repayment_frequency,
            eligibility=s.eligibility,
            source=s.source,
            source_url=s.source_url,
            last_verified_date=s.last_verified_date.isoformat() if s.last_verified_date else None,
            data_status=s.data_status,
        )
        for s in matched
    ]

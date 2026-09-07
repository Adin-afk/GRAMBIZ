"""
Deterministic financial engine.

CRITICAL RULE: nothing in this module is ever computed or altered by an LLM.
All values here are pure arithmetic driven by DB-stored assumptions
(FinancialAssumptionConfig, LoanScheme rows).
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.config import FinancialAssumptionConfig
from app.models.schemes import LoanScheme


class FinancialValidationError(Exception):
    pass


def get_active_assumptions(db: Session) -> FinancialAssumptionConfig:
    cfg = (
        db.query(FinancialAssumptionConfig)
        .filter(FinancialAssumptionConfig.active.is_(True))
        .order_by(FinancialAssumptionConfig.created_at.desc())
        .first()
    )
    if cfg is None:
        raise FinancialValidationError("No active financial assumption configuration found.")
    return cfg


def validate_available_margin(available_margin: float, cfg: FinancialAssumptionConfig) -> None:
    if available_margin is None:
        raise FinancialValidationError("Available margin capital is required.")
    if available_margin < 0:
        raise FinancialValidationError("Available margin capital cannot be negative.")
    if available_margin == 0:
        raise FinancialValidationError("Available margin capital must be greater than zero.")


def compute_project_cost_and_loan(
    available_margin: float,
    beneficiary_contribution_pct: float | None = None,
    db: Session | None = None,
) -> dict:
    """
    Project Cost = Available Margin / beneficiary_contribution_pct
    Loan Amount  = Project Cost * (1 - beneficiary_contribution_pct)
    """
    cfg = get_active_assumptions(db) if db is not None else None
    if beneficiary_contribution_pct is None:
        if cfg is None:
            raise FinancialValidationError("Beneficiary contribution percentage must be provided.")
        beneficiary_contribution_pct = cfg.default_beneficiary_contribution_pct

    if beneficiary_contribution_pct <= 0 or beneficiary_contribution_pct > 1:
        raise FinancialValidationError("Beneficiary contribution percentage must be between 0 and 1.")

    validate_available_margin(available_margin, cfg) if cfg else None

    project_cost = round(available_margin / beneficiary_contribution_pct, 2)
    loan_amount = round(project_cost - available_margin, 2)

    if cfg is not None:
        if project_cost < cfg.min_project_cost:
            raise FinancialValidationError(
                f"Resulting project cost (Rs. {project_cost:,.2f}) is below the minimum "
                f"supported project cost (Rs. {cfg.min_project_cost:,.2f})."
            )
        if project_cost > cfg.max_project_cost:
            raise FinancialValidationError(
                f"Resulting project cost (Rs. {project_cost:,.2f}) exceeds the maximum "
                f"supported project cost (Rs. {cfg.max_project_cost:,.2f}). Please consult a "
                f"financial advisor for large-scale project financing."
            )

    return {
        "available_margin": available_margin,
        "beneficiary_contribution_pct": beneficiary_contribution_pct,
        "project_cost": project_cost,
        "loan_amount": loan_amount,
    }


def find_matching_schemes(db: Session, project_cost: float) -> list[LoanScheme]:
    """Return active loan schemes whose project-cost band covers the given cost."""
    now = datetime.utcnow()
    q = (
        db.query(LoanScheme)
        .filter(LoanScheme.minimum_project_cost <= project_cost)
        .filter(LoanScheme.maximum_project_cost >= project_cost)
    )
    schemes = q.all()
    valid = []
    for s in schemes:
        if s.expiry_date is not None and s.expiry_date < now:
            continue
        valid.append(s)
    return valid


def compute_emi(principal: float, annual_interest_rate_pct: float, tenure_years: int) -> float:
    """Standard reducing-balance EMI formula. Deterministic, no external calls."""
    if principal <= 0:
        return 0.0
    monthly_rate = (annual_interest_rate_pct / 100) / 12
    n = tenure_years * 12
    if n <= 0:
        raise FinancialValidationError("Tenure must be at least 1 year.")
    if monthly_rate == 0:
        return round(principal / n, 2)
    emi = principal * monthly_rate * (1 + monthly_rate) ** n / ((1 + monthly_rate) ** n - 1)
    return round(emi, 2)


def build_repayment_schedule(
    principal: float,
    annual_interest_rate_pct: float,
    tenure_years: int,
    moratorium_months: int = 0,
    start_date: datetime | None = None,
) -> dict:
    """
    Generates a full month-by-month amortization schedule.
    Returns {installment, total_interest, total_repayment, schedule: [...]}.
    """
    start_date = start_date or datetime.utcnow()
    n = tenure_years * 12
    monthly_rate = (annual_interest_rate_pct / 100) / 12
    installment = compute_emi(principal, annual_interest_rate_pct, tenure_years)

    schedule = []
    balance = principal
    total_interest = 0.0

    # Moratorium period: interest-only or fully deferred, here modeled as
    # interest accrual with no principal repayment (standard convention).
    due_date = start_date
    for m in range(1, moratorium_months + 1):
        due_date = due_date + timedelta(days=30)
        interest = round(balance * monthly_rate, 2)
        total_interest += interest
        schedule.append(
            {
                "installment_number": m,
                "due_date": due_date.isoformat(),
                "principal_component": 0.0,
                "interest_component": interest,
                "remaining_balance": round(balance, 2),
                "phase": "MORATORIUM",
            }
        )

    for m in range(moratorium_months + 1, n + moratorium_months + 1):
        due_date = due_date + timedelta(days=30)
        interest = round(balance * monthly_rate, 2)
        principal_component = round(installment - interest, 2)
        if principal_component > balance:
            principal_component = round(balance, 2)
            this_installment = round(principal_component + interest, 2)
        else:
            this_installment = installment
        balance = round(balance - principal_component, 2)
        total_interest += interest
        schedule.append(
            {
                "installment_number": m,
                "due_date": due_date.isoformat(),
                "principal_component": principal_component,
                "interest_component": interest,
                "remaining_balance": max(balance, 0.0),
                "phase": "REPAYMENT",
            }
        )
        if balance <= 0:
            break

    total_repayment = round(principal + total_interest, 2)
    return {
        "installment": installment,
        "total_interest": round(total_interest, 2),
        "total_repayment": total_repayment,
        "schedule": schedule,
    }

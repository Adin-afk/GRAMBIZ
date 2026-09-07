from pydantic import BaseModel, Field


class FinancialCalculateRequest(BaseModel):
    available_margin: float = Field(..., description="Available margin capital in INR")
    beneficiary_contribution_pct: float | None = Field(
        None, description="Override the default contribution percentage (0-1). Optional."
    )
    scheme_id: str | None = Field(None, description="Explicit scheme to calculate against. Optional.")


class FinancialCalculateResponse(BaseModel):
    available_margin: float
    project_cost: float
    loan_amount: float
    beneficiary_contribution_pct: float
    matched_schemes: list[dict]
    selected_scheme: dict | None


class RepaymentRequest(BaseModel):
    principal: float
    annual_interest_rate_pct: float
    tenure_years: int
    moratorium_months: int = 0


class RepaymentResponse(BaseModel):
    installment: float
    total_interest: float
    total_repayment: float
    schedule: list[dict]


class SchemeOut(BaseModel):
    id: str
    scheme_name: str
    provider: str
    minimum_project_cost: float
    maximum_project_cost: float
    loan_percentage: float
    beneficiary_contribution: float
    maximum_loan: float
    interest_rate: float
    tenure_years: int
    moratorium_months: int
    repayment_frequency: str
    eligibility: str | None
    source: str | None
    source_url: str | None
    last_verified_date: str | None
    data_status: str

    class Config:
        from_attributes = True

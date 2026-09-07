from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    village_id: str
    available_capital: float = Field(..., gt=0)


class RecommendationItem(BaseModel):
    category_id: str
    category_name: str
    opportunity_score: float
    components: dict
    competitor_count_5km: int
    competitor_count_10km: int
    estimated_investment_low: float | None
    estimated_investment_high: float | None


class RecommendResponse(BaseModel):
    village_id: str
    available_capital: float
    recommendations: list[RecommendationItem]
    dataset_note: str


class AssessmentCreateRequest(BaseModel):
    village_id: str
    category_id: str
    available_capital: float = Field(..., gt=0)


class AssessmentOut(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: str
    village_id: str
    category_id: str | None
    available_capital: float
    opportunity_score: float | None
    market_analysis: dict | None
    competitor_analysis: dict | None
    financial_analysis: dict | None
    scheme_match: dict | None
    risk_assessment: dict | None
    swot: dict | None
    ai_explanation: str | None
    confidence_level: str
    dataset_version: str | None
    model_version: str | None

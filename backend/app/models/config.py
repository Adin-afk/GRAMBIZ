import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class ScoringWeightConfig(Base):
    """
    Opportunity-score component weights. Must sum to 1.0 across the active row.
    Editable only through the admin API - never hard-coded in the frontend.
    """

    __tablename__ = "scoring_weight_configs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    config_name: Mapped[str] = mapped_column(String(100), nullable=False, default="default")
    demand_weight: Mapped[float] = mapped_column(Float, default=0.20)
    competition_weight: Mapped[float] = mapped_column(Float, default=0.20)
    accessibility_weight: Mapped[float] = mapped_column(Float, default=0.15)
    cost_weight: Mapped[float] = mapped_column(Float, default=0.10)
    margin_weight: Mapped[float] = mapped_column(Float, default=0.15)
    market_access_weight: Mapped[float] = mapped_column(Float, default=0.10)
    seasonality_weight: Mapped[float] = mapped_column(Float, default=0.10)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FinancialAssumptionConfig(Base):
    """
    Deterministic financial-engine assumptions (contribution %, default scheme
    fallback etc). Editable through the admin API only.
    """

    __tablename__ = "financial_assumption_configs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    config_name: Mapped[str] = mapped_column(String(100), nullable=False, default="default")
    default_beneficiary_contribution_pct: Mapped[float] = mapped_column(Float, default=0.10)
    default_loan_pct: Mapped[float] = mapped_column(Float, default=0.90)
    min_project_cost: Mapped[float] = mapped_column(Float, default=0)
    max_project_cost: Mapped[float] = mapped_column(Float, default=5_000_000)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

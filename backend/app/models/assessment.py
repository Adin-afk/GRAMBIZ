import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class BusinessAssessment(Base):
    __tablename__ = "business_assessments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    village_id: Mapped[str] = mapped_column(ForeignKey("villages.id"), nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("business_categories.id"))
    available_capital: Mapped[float] = mapped_column(Float, nullable=False)

    opportunity_score: Mapped[float | None] = mapped_column(Float)
    demand_score: Mapped[float | None] = mapped_column(Float)
    competition_score: Mapped[float | None] = mapped_column(Float)
    accessibility_score: Mapped[float | None] = mapped_column(Float)
    margin_score: Mapped[float | None] = mapped_column(Float)
    market_access_score: Mapped[float | None] = mapped_column(Float)
    seasonality_score: Mapped[float | None] = mapped_column(Float)

    market_analysis: Mapped[dict | None] = mapped_column(JSONB)
    competitor_analysis: Mapped[dict | None] = mapped_column(JSONB)
    financial_analysis: Mapped[dict | None] = mapped_column(JSONB)
    scheme_match: Mapped[dict | None] = mapped_column(JSONB)
    risk_assessment: Mapped[dict | None] = mapped_column(JSONB)
    swot: Mapped[dict | None] = mapped_column(JSONB)
    ml_prediction: Mapped[dict | None] = mapped_column(JSONB)
    ai_explanation: Mapped[str | None] = mapped_column(Text)

    dataset_version: Mapped[str | None] = mapped_column(String(100))
    model_version: Mapped[str | None] = mapped_column(String(100))
    confidence_level: Mapped[str] = mapped_column(String(10), default="LOW")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketAssessment(Base):
    __tablename__ = "market_assessments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("business_assessments.id"), nullable=False)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"))
    nearby_markets: Mapped[dict | None] = mapped_column(JSONB)
    price_summary: Mapped[dict | None] = mapped_column(JSONB)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("business_assessments.id"), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(10), nullable=False)  # LOW|MEDIUM|HIGH
    risk_factors: Mapped[dict | None] = mapped_column(JSONB)


class SwotAssessment(Base):
    __tablename__ = "swot_assessments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("business_assessments.id"), nullable=False)
    strengths: Mapped[dict | None] = mapped_column(JSONB)
    weaknesses: Mapped[dict | None] = mapped_column(JSONB)
    opportunities: Mapped[dict | None] = mapped_column(JSONB)
    threats: Mapped[dict | None] = mapped_column(JSONB)


class LoanCalculation(Base):
    __tablename__ = "loan_calculations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    assessment_id: Mapped[str | None] = mapped_column(ForeignKey("business_assessments.id"))
    scheme_id: Mapped[str | None] = mapped_column(ForeignKey("loan_schemes.id"))
    available_margin: Mapped[float] = mapped_column(Float, nullable=False)
    project_cost: Mapped[float] = mapped_column(Float, nullable=False)
    loan_amount: Mapped[float] = mapped_column(Float, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False)
    tenure_years: Mapped[int] = mapped_column(Integer, nullable=False)
    installment: Mapped[float] = mapped_column(Float, nullable=False)
    total_interest: Mapped[float] = mapped_column(Float, nullable=False)
    total_repayment: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RepaymentSchedule(Base):
    __tablename__ = "repayment_schedules"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    loan_calculation_id: Mapped[str] = mapped_column(ForeignKey("loan_calculations.id"), nullable=False)
    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    principal_component: Mapped[float] = mapped_column(Float, nullable=False)
    interest_component: Mapped[float] = mapped_column(Float, nullable=False)
    remaining_balance: Mapped[float] = mapped_column(Float, nullable=False)


class MlDataset(Base):
    __tablename__ = "ml_datasets"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    dataset_version: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(300))
    record_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MlTrainingRun(Base):
    __tablename__ = "ml_training_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    dataset_id: Mapped[str | None] = mapped_column(ForeignKey("ml_datasets.id"))
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    metrics: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)


class MlModel(Base):
    __tablename__ = "ml_models"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    training_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    training_dataset_version: Mapped[str | None] = mapped_column(String(100))
    geographic_scope: Mapped[str | None] = mapped_column(String(200))
    feature_list: Mapped[dict | None] = mapped_column(JSONB)
    evaluation_metrics: Mapped[dict | None] = mapped_column(JSONB)
    model_file_location: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(default=False)


class MlPrediction(Base):
    __tablename__ = "ml_predictions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    model_id: Mapped[str | None] = mapped_column(ForeignKey("ml_models.id"))
    assessment_id: Mapped[str | None] = mapped_column(ForeignKey("business_assessments.id"))
    input_features: Mapped[dict | None] = mapped_column(JSONB)
    prediction: Mapped[dict | None] = mapped_column(JSONB)
    confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    doc_type: Mapped[str | None] = mapped_column(String(50))
    source_url: Mapped[str | None] = mapped_column(String(500))
    file_path: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


# NOTE: document_embeddings (pgvector column) is defined directly in the
# Alembic migration since GeoAlchemy2/pgvector column types are wired at
# the DB layer; see alembic/versions for the `vector(1536)` column.


class AiReport(Base):
    __tablename__ = "ai_reports"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("business_assessments.id"), nullable=False)
    report_json: Mapped[dict | None] = mapped_column(JSONB)
    generated_by: Mapped[str] = mapped_column(String(30), default="RULE_BASED")  # RULE_BASED | LLM
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

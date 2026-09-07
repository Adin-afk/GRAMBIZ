import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class LoanScheme(Base):
    __tablename__ = "loan_schemes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    scheme_name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(150), nullable=False)
    minimum_project_cost: Mapped[float] = mapped_column(Float, default=0)
    maximum_project_cost: Mapped[float] = mapped_column(Float, nullable=False)
    loan_percentage: Mapped[float] = mapped_column(Float, nullable=False)  # e.g. 0.90
    beneficiary_contribution: Mapped[float] = mapped_column(Float, nullable=False)  # e.g. 0.10
    maximum_loan: Mapped[float] = mapped_column(Float, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False)  # annual %, e.g. 8.5
    tenure_years: Mapped[int] = mapped_column(Integer, nullable=False)
    moratorium_months: Mapped[int] = mapped_column(Integer, default=0)
    repayment_frequency: Mapped[str] = mapped_column(String(20), default="MONTHLY")
    eligibility: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(200))
    source_url: Mapped[str | None] = mapped_column(String(500))
    effective_date: Mapped[datetime | None] = mapped_column(DateTime)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime)
    last_verified_date: Mapped[datetime | None] = mapped_column(DateTime)
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SchemeVersion(Base):
    __tablename__ = "scheme_versions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("loan_schemes.id"), nullable=False)
    version_label: Mapped[str] = mapped_column(String(50), nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SchemeEligibility(Base):
    __tablename__ = "scheme_eligibility"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("loan_schemes.id"), nullable=False)
    criterion: Mapped[str] = mapped_column(String(200), nullable=False)
    required_value: Mapped[str | None] = mapped_column(String(200))


class SchemeDocument(Base):
    __tablename__ = "scheme_documents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("loan_schemes.id"), nullable=False)
    document_name: Mapped[str] = mapped_column(String(200), nullable=False)
    document_url: Mapped[str | None] = mapped_column(String(500))

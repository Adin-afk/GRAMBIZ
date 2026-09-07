import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500))
    dataset_name: Mapped[str | None] = mapped_column(String(200))
    collection_date: Mapped[datetime | None] = mapped_column(DateTime)
    publication_date: Mapped[datetime | None] = mapped_column(DateTime)
    geographic_coverage: Mapped[str | None] = mapped_column(String(200))
    data_type: Mapped[str | None] = mapped_column(String(100))
    license: Mapped[str | None] = mapped_column(String(200))
    # HIGH | MEDIUM | LOW
    reliability: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    # VERIFIED | UNVERIFIED | NEEDS_REVIEW | EXPIRED
    verification_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    dataset_version: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    source_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    record_count: Mapped[int | None] = mapped_column(Integer)
    geographic_scope: Mapped[str | None] = mapped_column(String(200))
    processing_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DataUpdate(Base):
    __tablename__ = "data_updates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    record_id: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # INSERT/UPDATE/VERIFY/REJECT
    performed_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

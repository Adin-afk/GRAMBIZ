import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class State(Base):
    __tablename__ = "states"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    state_name: Mapped[str] = mapped_column(String(100), nullable=False)
    state_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    districts: Mapped[list["District"]] = relationship(back_populates="state")


class District(Base):
    __tablename__ = "districts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    state_id: Mapped[str] = mapped_column(ForeignKey("states.id"), nullable=False)
    district_name: Mapped[str] = mapped_column(String(100), nullable=False)
    official_name: Mapped[str | None] = mapped_column(String(150))
    official_code: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    state: Mapped["State"] = relationship(back_populates="districts")
    talukas: Mapped[list["Taluka"]] = relationship(back_populates="district")


class Taluka(Base):
    __tablename__ = "talukas"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    official_name: Mapped[str | None] = mapped_column(String(150))
    code: Mapped[str | None] = mapped_column(String(20))
    headquarters: Mapped[str | None] = mapped_column(String(100))
    area_sq_km: Mapped[float | None] = mapped_column(Float)
    total_villages: Mapped[int | None] = mapped_column(Integer)
    rural_villages: Mapped[int | None] = mapped_column(Integer)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    geometry = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    source_id: Mapped[str | None] = mapped_column(ForeignKey("data_sources.id"))
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    district: Mapped["District"] = relationship(back_populates="talukas")
    villages: Mapped[list["Village"]] = relationship(back_populates="taluka")


class Village(Base):
    __tablename__ = "villages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"), nullable=False)
    taluka_id: Mapped[str] = mapped_column(ForeignKey("talukas.id"), nullable=False)
    village_name: Mapped[str] = mapped_column(String(150), nullable=False)
    official_name: Mapped[str | None] = mapped_column(String(150))
    village_code: Mapped[str | None] = mapped_column(String(30))
    gram_panchayat: Mapped[str | None] = mapped_column(String(150))
    pincode: Mapped[str | None] = mapped_column(String(10))
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    geometry = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    # RURAL | URBAN | UNKNOWN
    area_type: Mapped[str] = mapped_column(String(10), nullable=False, default="UNKNOWN")

    population: Mapped[int | None] = mapped_column(Integer)
    households: Mapped[int | None] = mapped_column(Integer)
    male_population: Mapped[int | None] = mapped_column(Integer)
    female_population: Mapped[int | None] = mapped_column(Integer)
    literacy_rate: Mapped[float | None] = mapped_column(Float)
    agricultural_area: Mapped[float | None] = mapped_column(Float)

    source_id: Mapped[str | None] = mapped_column(ForeignKey("data_sources.id"))
    source_date: Mapped[datetime | None] = mapped_column(DateTime)
    verification_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")
    # VERIFIED | DEMO | ESTIMATED  -- explicit, user-visible data provenance flag
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    taluka: Mapped["Taluka"] = relationship(back_populates="villages")


class GramPanchayat(Base):
    __tablename__ = "gram_panchayats"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    village_id: Mapped[str] = mapped_column(ForeignKey("villages.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    sarpanch_name: Mapped[str | None] = mapped_column(String(150))
    contact: Mapped[str | None] = mapped_column(String(50))
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

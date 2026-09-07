import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class BusinessCategory(Base):
    __tablename__ = "business_categories"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    sector: Mapped[str | None] = mapped_column(String(50))  # AGRI | SERVICE | RETAIL | MANUFACTURING
    typical_min_investment: Mapped[float | None] = mapped_column(Float)
    typical_max_investment: Mapped[float | None] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BusinessCostTemplate(Base):
    __tablename__ = "business_cost_templates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String(150), nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=False)
    cost_type: Mapped[str] = mapped_column(String(20), default="CAPITAL")  # CAPITAL | OPERATING
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BusinessRevenueAssumption(Base):
    __tablename__ = "business_revenue_assumptions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"), nullable=False)
    monthly_revenue_low: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_revenue_high: Mapped[float] = mapped_column(Float, nullable=False)
    expected_margin_pct: Mapped[float] = mapped_column(Float, nullable=False)
    seasonality_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0-1, 1 = highly seasonal
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    village_id: Mapped[str] = mapped_column(ForeignKey("villages.id"), nullable=False)
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"), nullable=False)
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_name: Mapped[str | None] = mapped_column(String(150))
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    geometry = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    source: Mapped[str | None] = mapped_column(String(200))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")
    source_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    market_name: Mapped[str] = mapped_column(String(200), nullable=False)
    taluka_id: Mapped[str] = mapped_column(ForeignKey("talukas.id"), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    geometry = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    market_type: Mapped[str | None] = mapped_column(String(50))  # APMC | WEEKLY_BAZAAR | RETAIL_CLUSTER
    source: Mapped[str | None] = mapped_column(String(200))
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")
    source_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    market_id: Mapped[str] = mapped_column(ForeignKey("markets.id"), nullable=False)
    minimum_price: Mapped[float] = mapped_column(Float, nullable=False)
    average_price: Mapped[float] = mapped_column(Float, nullable=False)
    maximum_price: Mapped[float] = mapped_column(Float, nullable=False)
    price_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source: Mapped[str | None] = mapped_column(String(200))
    confidence: Mapped[str] = mapped_column(String(10), default="MEDIUM")  # HIGH|MEDIUM|LOW
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")


class PopulationStatistics(Base):
    __tablename__ = "population_statistics"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    village_id: Mapped[str] = mapped_column(ForeignKey("villages.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_population: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str | None] = mapped_column(String(200))
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")


class HouseholdStatistics(Base):
    __tablename__ = "household_statistics"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    village_id: Mapped[str] = mapped_column(ForeignKey("villages.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_households: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_household_size: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str | None] = mapped_column(String(200))
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")


class AgricultureStatistics(Base):
    __tablename__ = "agriculture_statistics"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    village_id: Mapped[str] = mapped_column(ForeignKey("villages.id"), nullable=False)
    major_crop: Mapped[str | None] = mapped_column(String(100))
    irrigated_area: Mapped[float | None] = mapped_column(Float)
    rainfed_area: Mapped[float | None] = mapped_column(Float)
    agricultural_activity: Mapped[str | None] = mapped_column(String(200))
    source: Mapped[str | None] = mapped_column(String(200))
    source_date: Mapped[datetime | None] = mapped_column(DateTime)
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")


class LivestockStatistics(Base):
    __tablename__ = "livestock_statistics"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    village_id: Mapped[str] = mapped_column(ForeignKey("villages.id"), nullable=False)
    cattle_count: Mapped[int | None] = mapped_column(Integer)
    buffalo_count: Mapped[int | None] = mapped_column(Integer)
    goat_count: Mapped[int | None] = mapped_column(Integer)
    sheep_count: Mapped[int | None] = mapped_column(Integer)
    poultry_count: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str | None] = mapped_column(String(200))
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")


class InfrastructureStatistics(Base):
    __tablename__ = "infrastructure_statistics"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    village_id: Mapped[str] = mapped_column(ForeignKey("villages.id"), nullable=False)
    road_access: Mapped[bool | None] = mapped_column(Boolean)
    electricity: Mapped[bool | None] = mapped_column(Boolean)
    internet: Mapped[bool | None] = mapped_column(Boolean)
    drinking_water: Mapped[bool | None] = mapped_column(Boolean)
    bank_available: Mapped[bool | None] = mapped_column(Boolean)
    atm_available: Mapped[bool | None] = mapped_column(Boolean)
    primary_health_center: Mapped[bool | None] = mapped_column(Boolean)
    school_available: Mapped[bool | None] = mapped_column(Boolean)
    source: Mapped[str | None] = mapped_column(String(200))
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")

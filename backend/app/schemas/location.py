from datetime import datetime

from pydantic import BaseModel


class TalukaOut(BaseModel):
    id: str
    name: str
    headquarters: str | None
    total_villages: int | None
    rural_villages: int | None
    latitude: float | None
    longitude: float | None

    class Config:
        from_attributes = True


class VillageOut(BaseModel):
    id: str
    village_name: str
    taluka_id: str
    gram_panchayat: str | None
    area_type: str
    population: int | None
    households: int | None
    latitude: float
    longitude: float
    data_status: str
    verification_status: str

    class Config:
        from_attributes = True


class BusinessCategoryOut(BaseModel):
    id: str
    name: str
    description: str | None
    sector: str | None
    typical_min_investment: float | None
    typical_max_investment: float | None

    class Config:
        from_attributes = True


class NearbyBusinessOut(BaseModel):
    id: str
    business_name: str
    owner_name: str | None
    category_name: str
    village_name: str
    taluka_name: str
    latitude: float
    longitude: float
    distance_km: float
    data_status: str
    source: str | None
    source_date: datetime | None


class NearbyMarketOut(BaseModel):
    id: str
    market_name: str
    market_type: str | None
    taluka_name: str
    latitude: float
    longitude: float
    distance_km: float
    data_status: str
    source: str | None
    source_date: datetime | None


class ProductPriceOut(BaseModel):
    product_name: str
    market_name: str
    minimum_price: float
    average_price: float
    maximum_price: float
    unit: str
    price_date: datetime
    source: str | None
    confidence: str
    data_status: str

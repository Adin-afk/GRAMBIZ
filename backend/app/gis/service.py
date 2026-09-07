"""
GIS service. All radius/distance queries execute inside PostgreSQL via
PostGIS (ST_DWithin / ST_Distance on geography) - we never fetch the full
businesses/markets tables into Python to compute distance client-side.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session

# ST_DWithin on ::geography interprets the radius in meters and accounts for
# the earth's curvature, which is what we want for 5km / 10km rural queries.

NEARBY_BUSINESSES_SQL = text(
    """
    SELECT
        b.id,
        b.business_name,
        b.owner_name,
        bc.name AS category_name,
        v.village_name,
        t.name AS taluka_name,
        b.latitude,
        b.longitude,
        b.data_status,
        b.source,
        b.source_date,
        ST_Distance(b.geometry::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) AS distance_m
    FROM businesses b
    JOIN business_categories bc ON bc.id = b.category_id
    JOIN villages v ON v.id = b.village_id
    JOIN talukas t ON t.id = v.taluka_id
    WHERE b.status = 'ACTIVE'
      AND (:category_id IS NULL OR b.category_id = :category_id)
      AND ST_DWithin(b.geometry::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_m)
    ORDER BY distance_m ASC
    """
)

NEARBY_MARKETS_SQL = text(
    """
    SELECT
        m.id,
        m.market_name,
        m.market_type,
        t.name AS taluka_name,
        m.latitude,
        m.longitude,
        m.data_status,
        m.source,
        m.source_date,
        ST_Distance(m.geometry::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) AS distance_m
    FROM markets m
    JOIN talukas t ON t.id = m.taluka_id
    WHERE ST_DWithin(m.geometry::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_m)
    ORDER BY distance_m ASC
    """
)

NEARBY_VILLAGES_SQL = text(
    """
    SELECT
        v.id,
        v.village_name,
        v.area_type,
        v.population,
        t.name AS taluka_name,
        v.latitude,
        v.longitude,
        ST_Distance(v.geometry::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) AS distance_m
    FROM villages v
    JOIN talukas t ON t.id = v.taluka_id
    WHERE ST_DWithin(v.geometry::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_m)
      AND v.id != :exclude_village_id
    ORDER BY distance_m ASC
    """
)

COMPETITOR_COUNT_SQL = text(
    """
    SELECT COUNT(*) AS cnt
    FROM businesses b
    WHERE b.status = 'ACTIVE'
      AND b.category_id = :category_id
      AND ST_DWithin(b.geometry::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_m)
    """
)


def _row_to_json_safe(row: dict) -> dict:
    """Raw SQL rows can contain psycopg2 UUID objects (from native uuid
    columns) and Decimal/datetime values that aren't JSON-serializable when
    stored into JSONB fields. Normalize them to plain str/float."""
    import datetime as _dt
    import decimal
    import uuid as _uuid

    out = {}
    for k, v in row.items():
        if isinstance(v, _uuid.UUID):
            out[k] = str(v)
        elif isinstance(v, decimal.Decimal):
            out[k] = float(v)
        elif isinstance(v, (_dt.datetime, _dt.date)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def get_nearby_businesses(db: Session, lat: float, lng: float, radius_km: float, category_id: str | None = None):
    rows = db.execute(
        NEARBY_BUSINESSES_SQL,
        {"lat": lat, "lng": lng, "radius_m": radius_km * 1000, "category_id": category_id},
    ).mappings().all()
    return [_row_to_json_safe(dict(r) | {"distance_km": round(r["distance_m"] / 1000, 2)}) for r in rows]


def get_nearby_markets(db: Session, lat: float, lng: float, radius_km: float):
    rows = db.execute(
        NEARBY_MARKETS_SQL, {"lat": lat, "lng": lng, "radius_m": radius_km * 1000}
    ).mappings().all()
    return [_row_to_json_safe(dict(r) | {"distance_km": round(r["distance_m"] / 1000, 2)}) for r in rows]


def get_nearby_villages(db: Session, lat: float, lng: float, radius_km: float, exclude_village_id: str):
    rows = db.execute(
        NEARBY_VILLAGES_SQL,
        {"lat": lat, "lng": lng, "radius_m": radius_km * 1000, "exclude_village_id": exclude_village_id},
    ).mappings().all()
    return [_row_to_json_safe(dict(r) | {"distance_km": round(r["distance_m"] / 1000, 2)}) for r in rows]


def get_competitor_count(db: Session, lat: float, lng: float, radius_km: float, category_id: str) -> int:
    result = db.execute(
        COMPETITOR_COUNT_SQL,
        {"lat": lat, "lng": lng, "radius_m": radius_km * 1000, "category_id": category_id},
    ).scalar()
    return int(result or 0)


def competitor_density(count_5km: int, count_10km: int) -> dict:
    """
    Density = competitors per sq. km within each ring.
    5km ring area = pi * 5^2 ; 10km ring area = pi * 10^2
    """
    area_5km = 3.14159265 * 5 * 5
    area_10km = 3.14159265 * 10 * 10
    return {
        "density_5km_per_sqkm": round(count_5km / area_5km, 4),
        "density_10km_per_sqkm": round(count_10km / area_10km, 4),
    }

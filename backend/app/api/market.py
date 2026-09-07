from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.gis import service as gis_service
from app.models.business import Product, ProductPrice
from app.models.geography import Village
from app.schemas.location import NearbyMarketOut, ProductPriceOut

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/nearby", response_model=list[NearbyMarketOut])
def nearby_markets(
    village_id: str = Query(...),
    radius_km: float = Query(10.0, ge=0.5, le=25.0),
    db: Session = Depends(get_db),
):
    village = db.get(Village, village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error_code": "LOCATION_NOT_FOUND", "message": "The selected village could not be found."},
        )
    return gis_service.get_nearby_markets(db, lat=village.latitude, lng=village.longitude, radius_km=radius_km)


@router.get("/prices", response_model=list[ProductPriceOut])
def product_prices(product_name: str | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(ProductPrice, Product).join(Product, Product.id == ProductPrice.product_id)
    if product_name:
        q = q.filter(Product.name.ilike(f"%{product_name}%"))
    rows = q.order_by(ProductPrice.price_date.desc()).limit(100).all()
    out = []
    for price, product in rows:
        market = price.market_id  # id only; join market_name in analysis endpoint if needed
        out.append(
            ProductPriceOut(
                product_name=product.name,
                market_name="",
                minimum_price=price.minimum_price,
                average_price=price.average_price,
                maximum_price=price.maximum_price,
                unit=product.unit,
                price_date=price.price_date,
                source=price.source,
                confidence=price.confidence,
                data_status=price.data_status,
            )
        )
    return out


@router.get("/analysis")
def market_analysis(village_id: str = Query(...), radius_km: float = Query(10.0), db: Session = Depends(get_db)):
    """Combined nearby-markets + price summary view used by the advisory report."""
    village = db.get(Village, village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error_code": "LOCATION_NOT_FOUND", "message": "The selected village could not be found."},
        )
    markets = gis_service.get_nearby_markets(db, lat=village.latitude, lng=village.longitude, radius_km=radius_km)
    market_ids = [m["id"] for m in markets]
    prices = []
    if market_ids:
        rows = (
            db.query(ProductPrice, Product)
            .join(Product, Product.id == ProductPrice.product_id)
            .filter(ProductPrice.market_id.in_(market_ids))
            .order_by(ProductPrice.price_date.desc())
            .limit(50)
            .all()
        )
        for price, product in rows:
            prices.append(
                {
                    "product_name": product.name,
                    "unit": product.unit,
                    "minimum_price": price.minimum_price,
                    "average_price": price.average_price,
                    "maximum_price": price.maximum_price,
                    "price_date": price.price_date.isoformat(),
                    "source": price.source,
                    "confidence": price.confidence,
                    "data_status": price.data_status,
                }
            )
    return {
        "village_id": village_id,
        "radius_km": radius_km,
        "market_count": len(markets),
        "markets": markets,
        "recent_prices": prices,
    }

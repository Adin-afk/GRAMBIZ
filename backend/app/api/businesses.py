from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.gis import service as gis_service
from app.models.business import BusinessCategory
from app.models.geography import Village
from app.schemas.location import BusinessCategoryOut, NearbyBusinessOut

router = APIRouter(prefix="/api", tags=["businesses"])


@router.get("/business-categories", response_model=list[BusinessCategoryOut])
def list_business_categories(db: Session = Depends(get_db)):
    return db.query(BusinessCategory).filter(BusinessCategory.active.is_(True)).order_by(BusinessCategory.name).all()


@router.get("/businesses/nearby", response_model=list[NearbyBusinessOut])
def nearby_businesses(
    village_id: str = Query(...),
    radius_km: float = Query(5.0, ge=0.5, le=10.0),
    category_id: str | None = Query(None),
    db: Session = Depends(get_db),
):
    village = db.get(Village, village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error_code": "LOCATION_NOT_FOUND", "message": "The selected village could not be found."},
        )
    results = gis_service.get_nearby_businesses(
        db, lat=village.latitude, lng=village.longitude, radius_km=radius_km, category_id=category_id
    )
    return results

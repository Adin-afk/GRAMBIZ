from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.geography import District, State, Taluka, Village
from app.schemas.location import TalukaOut, VillageOut

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("/talukas", response_model=list[TalukaOut])
def list_talukas(db: Session = Depends(get_db)):
    """Returns the configured Solapur taluka list. Never hard-coded in the frontend."""
    talukas = db.query(Taluka).filter(Taluka.active.is_(True)).order_by(Taluka.name).all()
    return talukas


@router.get("/villages", response_model=list[VillageOut])
def list_villages(
    taluka_id: str = Query(...),
    area_type: str = Query("RURAL", description="RURAL | URBAN | UNKNOWN | ALL"),
    db: Session = Depends(get_db),
):
    q = db.query(Village).filter(Village.taluka_id == taluka_id)
    if area_type != "ALL":
        q = q.filter(Village.area_type == area_type)
    villages = q.order_by(Village.village_name).all()
    return villages


@router.get("/villages/{village_id}", response_model=VillageOut)
def get_village(village_id: str, db: Session = Depends(get_db)):
    village = db.get(Village, village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error_code": "LOCATION_NOT_FOUND", "message": "The selected village could not be found."},
        )
    return village


@router.get("/search", response_model=list[VillageOut])
def search_locations(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    like = f"%{q}%"
    results = (
        db.query(Village)
        .filter(or_(Village.village_name.ilike(like), Village.gram_panchayat.ilike(like)))
        .limit(25)
        .all()
    )
    return results

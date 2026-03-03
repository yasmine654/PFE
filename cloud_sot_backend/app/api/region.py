from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.validators import validate_fk_exists
from app.models.provider import Provider

from app.core.database import get_db
from app.schemas.region import RegionCreate, RegionResponse, RegionUpdate
from app.crud import region as crud_region
from app.models.region import Region

router = APIRouter(prefix="/regions", tags=["Regions"])


# ✅ CREATE
@router.post("/", response_model=RegionResponse)
def create_region(region: RegionCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, Provider, "Provider", region.provider_id)

    return crud_region.create_region(db, region)

# ✅ GET ALL
@router.get("/", response_model=list[RegionResponse])
def read_regions(db: Session = Depends(get_db)):
    return crud_region.get_regions(db)


# ✅ GET ONE
@router.get("/{region_id}", response_model=RegionResponse)
def read_region(region_id: int, db: Session = Depends(get_db)):
    region = crud_region.get_region(db, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


# 🔒 DELETE NORMAL (bloqué si dépendances)
@router.delete("/{region_id}")
def delete_region(region_id: int, db: Session = Depends(get_db)):

    region_obj = db.query(Region).filter(
        Region.region_id == region_id
    ).first()

    if not region_obj:
        raise HTTPException(status_code=404, detail="Region not found")

    # 🔒 Vérification via ORM relationships
    if (
        region_obj.availability_zones
        or region_obj.vpcs
        or region_obj.vms
        or region_obj.elastic_ips
    ):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete region with existing dependencies. Use /force."
        )

    db.delete(region_obj)
    db.commit()

    return {"message": "Region deleted"}


# 💣 DELETE FORCÉ (cascade ORM fait tout)
@router.delete("/{region_id}/force")
def force_delete_region(region_id: int, db: Session = Depends(get_db)):

    region_obj = db.query(Region).filter(
        Region.region_id == region_id
    ).first()

    if not region_obj:
        raise HTTPException(status_code=404, detail="Region not found")

    db.delete(region_obj)   # 🔥 ORM cascade supprime enfants automatiquement
    db.commit()

    return {"message": "Region force deleted"}


# ✅ UPDATE
@router.put("/{region_id}", response_model=RegionResponse)
def update_region(region_id: int, region: RegionUpdate, db: Session = Depends(get_db)):
    updated = crud_region.update_region(db, region_id, region)
    if not updated:
        raise HTTPException(status_code=404, detail="Region not found")
    return updated
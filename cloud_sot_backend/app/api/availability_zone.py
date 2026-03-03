from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists
from app.schemas.availability_zone import (
    AvailabilityZoneCreate,
    AvailabilityZoneResponse,
    AvailabilityZoneUpdate
)
from app.crud import availability_zone as crud_az
from app.models.availability_zone import AvailabilityZone
from app.models.region import Region

router = APIRouter(prefix="/availability-zones", tags=["Availability Zones"])


# ✅ CREATE
@router.post("/", response_model=AvailabilityZoneResponse)
def create_availability_zone(az: AvailabilityZoneCreate, db: Session = Depends(get_db)):

    # 🔍 Vérifier parent Region
    validate_fk_exists(db, Region, "Region", az.region_id)

    return crud_az.create_availability_zone(db, az)


# ✅ GET ALL
@router.get("/", response_model=list[AvailabilityZoneResponse])
def read_availability_zones(db: Session = Depends(get_db)):
    return crud_az.get_availability_zones(db)


# ✅ GET ONE
@router.get("/{az_id}", response_model=AvailabilityZoneResponse)
def read_availability_zone(az_id: int, db: Session = Depends(get_db)):
    az = crud_az.get_availability_zone(db, az_id)
    if not az:
        raise HTTPException(status_code=404, detail="Availability Zone not found")
    return az


# 🔒 DELETE NORMAL
@router.delete("/{az_id}")
def delete_availability_zone(az_id: int, db: Session = Depends(get_db)):

    az = db.query(AvailabilityZone).filter(
        AvailabilityZone.az_id == az_id
    ).first()

    if not az:
        raise HTTPException(status_code=404, detail="Availability Zone not found")

    if az.subnets or az.vms:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete Availability Zone with dependencies. Use /force."
        )

    db.delete(az)
    db.commit()

    return {"message": "Availability Zone deleted"}


# 💣 DELETE FORCÉ
@router.delete("/{az_id}/force")
def force_delete_availability_zone(az_id: int, db: Session = Depends(get_db)):

    az = db.query(AvailabilityZone).filter(
        AvailabilityZone.az_id == az_id
    ).first()

    if not az:
        raise HTTPException(status_code=404, detail="Availability Zone not found")

    db.delete(az)   # 🔥 cascade ORM supprime subnets + vms
    db.commit()

    return {"message": "Availability Zone force deleted"}


# ✅ UPDATE
@router.put("/{az_id}", response_model=AvailabilityZoneResponse)
def update_availability_zone(az_id: int, az_update: AvailabilityZoneUpdate, db: Session = Depends(get_db)):

    # Si on change le parent region
    if az_update.region_id is not None:
        validate_fk_exists(db, Region, "Region", az_update.region_id)

    updated = crud_az.update_availability_zone(db, az_id, az_update)

    if not updated:
        raise HTTPException(status_code=404, detail="Availability Zone not found")

    return updated
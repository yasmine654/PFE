from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.volume import (
    VolumeCreate,
    VolumeResponse,
    VolumeUpdate
)

from app.crud import volume as crud_volume

from app.models.volume import Volume
from app.models.vm import VM

router = APIRouter(prefix="/volumes", tags=["Volumes"])


# CREATE
@router.post("/", response_model=VolumeResponse)
def create_volume(volume: VolumeCreate, db: Session = Depends(get_db)):

    if volume.vm_id is not None:
        validate_fk_exists(db, VM, "VM", volume.vm_id)

    return crud_volume.create_volume(db, volume)


# GET ALL
@router.get("/", response_model=list[VolumeResponse])
def read_volumes(db: Session = Depends(get_db)):

    return crud_volume.get_volumes(db)


# GET ONE
@router.get("/{volume_id}", response_model=VolumeResponse)
def read_volume(volume_id: int, db: Session = Depends(get_db)):

    volume = crud_volume.get_volume(db, volume_id)

    if not volume:
        raise HTTPException(status_code=404, detail="Volume not found")

    return volume


# DELETE NORMAL
@router.delete("/{volume_id}")
def delete_volume(volume_id: int, db: Session = Depends(get_db)):

    deleted = crud_volume.delete_volume(db, volume_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Volume not found")

    return {"message": "Volume deleted"}


# DELETE FORCE
@router.delete("/{volume_id}/force")
def force_delete_volume(volume_id: int, db: Session = Depends(get_db)):

    deleted = crud_volume.delete_volume(db, volume_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Volume not found")

    return {"message": "Volume force deleted"}


# UPDATE
@router.put("/{volume_id}", response_model=VolumeResponse)
def update_volume(volume_id: int, volume_update: VolumeUpdate, db: Session = Depends(get_db)):

    if volume_update.vm_id is not None:
        validate_fk_exists(db, VM, "VM", volume_update.vm_id)

    updated = crud_volume.update_volume(db, volume_id, volume_update)

    if not updated:
        raise HTTPException(status_code=404, detail="Volume not found")

    return updated
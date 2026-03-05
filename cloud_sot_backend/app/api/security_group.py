from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.security_group import (
    SecurityGroupCreate,
    SecurityGroupResponse,
    SecurityGroupUpdate
)

from app.crud import security_group as crud_sg

from app.models.security_group import SecurityGroup
from app.models.vm import VM

router = APIRouter(prefix="/security_groups", tags=["Security Groups"])


# CREATE
@router.post("/", response_model=SecurityGroupResponse)
def create_security_group(sg: SecurityGroupCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, VM, "VM", sg.vm_id)

    return crud_sg.create_security_group(db, sg)


# GET ALL
@router.get("/", response_model=list[SecurityGroupResponse])
def read_security_groups(db: Session = Depends(get_db)):

    return crud_sg.get_security_groups(db)


# GET ONE
@router.get("/{sg_id}", response_model=SecurityGroupResponse)
def read_security_group(sg_id: int, db: Session = Depends(get_db)):

    sg = crud_sg.get_security_group(db, sg_id)

    if not sg:
        raise HTTPException(status_code=404, detail="Security Group not found")

    return sg


# DELETE NORMAL
@router.delete("/{sg_id}")
def delete_security_group(sg_id: int, db: Session = Depends(get_db)):

    sg = crud_sg.delete_security_group(db, sg_id)

    if not sg:
        raise HTTPException(status_code=404, detail="Security Group not found")

    return {"message": "Security Group deleted"}


# DELETE FORCE
@router.delete("/{sg_id}/force")
def force_delete_security_group(sg_id: int, db: Session = Depends(get_db)):

    sg = crud_sg.delete_security_group(db, sg_id)

    if not sg:
        raise HTTPException(status_code=404, detail="Security Group not found")

    return {"message": "Security Group force deleted"}


# UPDATE
@router.put("/{sg_id}", response_model=SecurityGroupResponse)
def update_security_group(sg_id: int, sg_update: SecurityGroupUpdate, db: Session = Depends(get_db)):

    if sg_update.vm_id is not None:
        validate_fk_exists(db, VM, "VM", sg_update.vm_id)

    updated = crud_sg.update_security_group(db, sg_id, sg_update)

    if not updated:
        raise HTTPException(status_code=404, detail="Security Group not found")

    return updated
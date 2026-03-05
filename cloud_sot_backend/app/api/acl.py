from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.acl import ACLCreate, ACLResponse, ACLUpdate
from app.crud import acl as crud_acl

from app.models.acl import ACL
from app.models.subnet import Subnet

router = APIRouter(prefix="/acls", tags=["ACLs"])


# CREATE
@router.post("/", response_model=ACLResponse)
def create_acl(acl: ACLCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, Subnet, "Subnet", acl.subnet_id)

    return crud_acl.create_acl(db, acl)


# GET ALL
@router.get("/", response_model=list[ACLResponse])
def read_acls(db: Session = Depends(get_db)):

    return crud_acl.get_acls(db)


# GET ONE
@router.get("/{acl_id}", response_model=ACLResponse)
def read_acl(acl_id: int, db: Session = Depends(get_db)):

    acl = crud_acl.get_acl(db, acl_id)

    if not acl:
        raise HTTPException(status_code=404, detail="ACL not found")

    return acl


# DELETE NORMAL
@router.delete("/{acl_id}")
def delete_acl(acl_id: int, db: Session = Depends(get_db)):

    acl = db.query(ACL).filter(
        ACL.acl_id == acl_id
    ).first()

    if not acl:
        raise HTTPException(status_code=404, detail="ACL not found")

    db.delete(acl)
    db.commit()

    return {"message": "ACL deleted"}


# DELETE FORCE
@router.delete("/{acl_id}/force")
def force_delete_acl(acl_id: int, db: Session = Depends(get_db)):

    acl = db.query(ACL).filter(
        ACL.acl_id == acl_id
    ).first()

    if not acl:
        raise HTTPException(status_code=404, detail="ACL not found")

    db.delete(acl)
    db.commit()

    return {"message": "ACL force deleted"}


# UPDATE
@router.put("/{acl_id}", response_model=ACLResponse)
def update_acl(acl_id: int, acl_update: ACLUpdate, db: Session = Depends(get_db)):

    if acl_update.subnet_id is not None:
        validate_fk_exists(db, Subnet, "Subnet", acl_update.subnet_id)

    updated = crud_acl.update_acl(db, acl_id, acl_update)

    if not updated:
        raise HTTPException(status_code=404, detail="ACL not found")

    return updated
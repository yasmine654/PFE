from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists
from app.schemas.subnet import SubnetCreate, SubnetResponse, SubnetUpdate
from app.crud import subnet as crud_subnet
from app.models.subnet import Subnet
from app.models.vpc import VPC
from app.models.availability_zone import AvailabilityZone

router = APIRouter(prefix="/subnets", tags=["Subnets"])


# ✅ CREATE
@router.post("/", response_model=SubnetResponse)
def create_subnet(subnet: SubnetCreate, db: Session = Depends(get_db)):

    # 🔍 Vérifier parents
    validate_fk_exists(db, VPC, "VPC", subnet.vpc_id)
    validate_fk_exists(db, AvailabilityZone, "Availability Zone", subnet.az_id)

    return crud_subnet.create_subnet(db, subnet)


# ✅ GET ALL
@router.get("/", response_model=list[SubnetResponse])
def read_subnets(db: Session = Depends(get_db)):
    return crud_subnet.get_subnets(db)


# ✅ GET ONE
@router.get("/{subnet_id}", response_model=SubnetResponse)
def read_subnet(subnet_id: int, db: Session = Depends(get_db)):
    subnet = crud_subnet.get_subnet(db, subnet_id)
    if not subnet:
        raise HTTPException(status_code=404, detail="Subnet not found")
    return subnet


# 🔒 DELETE NORMAL
@router.delete("/{subnet_id}")
def delete_subnet(subnet_id: int, db: Session = Depends(get_db)):

    subnet = db.query(Subnet).filter(
        Subnet.subnet_id == subnet_id
    ).first()

    if not subnet:
        raise HTTPException(status_code=404, detail="Subnet not found")

    if (
        subnet.vms
        or subnet.acls
        or subnet.load_balancers
        or subnet.vpn_gateways
        or subnet.wafs
    ):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete Subnet with existing dependencies. Use /force."
        )

    db.delete(subnet)
    db.commit()

    return {"message": "Subnet deleted"}


# 💣 DELETE FORCÉ
@router.delete("/{subnet_id}/force")
def force_delete_subnet(subnet_id: int, db: Session = Depends(get_db)):

    subnet = db.query(Subnet).filter(
        Subnet.subnet_id == subnet_id
    ).first()

    if not subnet:
        raise HTTPException(status_code=404, detail="Subnet not found")

    db.delete(subnet)  # 🔥 cascade ORM supprime enfants
    db.commit()

    return {"message": "Subnet force deleted"}


# ✅ UPDATE
@router.put("/{subnet_id}", response_model=SubnetResponse)
def update_subnet(subnet_id: int, subnet_update: SubnetUpdate, db: Session = Depends(get_db)):

    if subnet_update.vpc_id is not None:
        validate_fk_exists(db, VPC, "VPC", subnet_update.vpc_id)

    if subnet_update.az_id is not None:
        validate_fk_exists(db, AvailabilityZone, "Availability Zone", subnet_update.az_id)

    updated = crud_subnet.update_subnet(db, subnet_id, subnet_update)

    if not updated:
        raise HTTPException(status_code=404, detail="Subnet not found")

    return updated
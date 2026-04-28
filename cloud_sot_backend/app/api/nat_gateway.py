from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.nat_gateway import (
    NATGatewayCreate,
    NATGatewayResponse,
    NATGatewayUpdate
)

from app.crud import nat_gateway as crud_nat

from app.models.nat_gateway import NATGateway
from app.models.vpc import VPC
from app.models.subnet import Subnet

router = APIRouter(prefix="/nat_gateways", tags=["NAT Gateways"])


# CREATE
@router.post("/", response_model=NATGatewayResponse)
def create_nat_gateway(nat: NATGatewayCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, VPC, "VPC", nat.vpc_id)
    validate_fk_exists(db, Subnet, "Subnet", nat.subnet_id)

    return crud_nat.create_nat_gateway(db, nat)


# GET ALL
@router.get("/", response_model=list[NATGatewayResponse])
def read_nat_gateways(db: Session = Depends(get_db)):

    return crud_nat.get_nat_gateways(db)


# GET ONE
@router.get("/{nat_id}", response_model=NATGatewayResponse)
def read_nat_gateway(nat_id: int, db: Session = Depends(get_db)):

    nat = crud_nat.get_nat_gateway(db, nat_id)

    if not nat:
        raise HTTPException(status_code=404, detail="NAT Gateway not found")

    return nat


# DELETE NORMAL
@router.delete("/{nat_id}")
def delete_nat_gateway(nat_id: int, db: Session = Depends(get_db)):

    nat = db.query(NATGateway).filter(
        NATGateway.nat_id == nat_id
    ).first()

    if not nat:
        raise HTTPException(status_code=404, detail="NAT Gateway not found")

    db.delete(nat)
    db.commit()

    return {"message": "NAT Gateway deleted"}


# DELETE FORCE
@router.delete("/{nat_id}/force")
def force_delete_nat_gateway(nat_id: int, db: Session = Depends(get_db)):

    nat = db.query(NATGateway).filter(
        NATGateway.nat_id == nat_id
    ).first()

    if not nat:
        raise HTTPException(status_code=404, detail="NAT Gateway not found")

    db.delete(nat)
    db.commit()

    return {"message": "NAT Gateway force deleted"}


# UPDATE
@router.put("/{nat_id}", response_model=NATGatewayResponse)
def update_nat_gateway(nat_id: int, nat_update: NATGatewayUpdate, db: Session = Depends(get_db)):

    # ✅ VALIDATION AVANT UPDATE
    if nat_update.vpc_id is not None:
        validate_fk_exists(db, VPC, "VPC", nat_update.vpc_id)

    if nat_update.subnet_id is not None:
        validate_fk_exists(db, Subnet, "Subnet", nat_update.subnet_id)

    updated = crud_nat.update_nat_gateway(db, nat_id, nat_update)

    if not updated:
        raise HTTPException(status_code=404, detail="NAT Gateway not found")

    return updated

    
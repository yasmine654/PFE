from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.vpc_peering import (
    VPCPeeringCreate,
    VPCPeeringResponse,
    VPCPeeringUpdate
)

from app.crud import vpc_peering as crud_peering

from app.models.vpc_peering import VPCPeering
from app.models.tenant import Tenant
from app.models.provider import Provider
from app.models.vpc import VPC

router = APIRouter(prefix="/vpc_peerings", tags=["VPC Peerings"])


# CREATE
@router.post("/", response_model=VPCPeeringResponse)
def create_vpc_peering(peering: VPCPeeringCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, Tenant, "Tenant", peering.tenant_id)
    validate_fk_exists(db, Provider, "Provider", peering.provider_id)
    validate_fk_exists(db, VPC, "Source VPC", peering.vpc_source_id)
    validate_fk_exists(db, VPC, "Target VPC", peering.vpc_target_id)

    if peering.vpc_source_id == peering.vpc_target_id:
        raise HTTPException(
            status_code=400,
            detail="Source VPC and Target VPC cannot be the same"
        )

    return crud_peering.create_vpc_peering(db, peering)


# GET ALL
@router.get("/", response_model=list[VPCPeeringResponse])
def read_peerings(db: Session = Depends(get_db)):
    return crud_peering.get_peerings(db)


# GET ONE
@router.get("/{peering_id}", response_model=VPCPeeringResponse)
def read_peering(peering_id: int, db: Session = Depends(get_db)):

    peering = crud_peering.get_peering(db, peering_id)

    if not peering:
        raise HTTPException(status_code=404, detail="VPC Peering not found")

    return peering


# DELETE NORMAL
@router.delete("/{peering_id}")
def delete_peering(peering_id: int, db: Session = Depends(get_db)):

    peering = db.query(VPCPeering).filter(
        VPCPeering.peering_id == peering_id
    ).first()

    if not peering:
        raise HTTPException(status_code=404, detail="VPC Peering not found")

    db.delete(peering)
    db.commit()

    return {"message": "VPC Peering deleted"}


# DELETE FORCE (même chose car pas d'enfants)
@router.delete("/{peering_id}/force")
def force_delete_peering(peering_id: int, db: Session = Depends(get_db)):

    peering = db.query(VPCPeering).filter(
        VPCPeering.peering_id == peering_id
    ).first()

    if not peering:
        raise HTTPException(status_code=404, detail="VPC Peering not found")

    db.delete(peering)
    db.commit()

    return {"message": "VPC Peering force deleted"}


# UPDATE
@router.put("/{peering_id}", response_model=VPCPeeringResponse)
def update_peering(peering_id: int, peering_update: VPCPeeringUpdate, db: Session = Depends(get_db)):

    if peering_update.tenant_id is not None:
        validate_fk_exists(db, Tenant, "Tenant", peering_update.tenant_id)

    if peering_update.provider_id is not None:
        validate_fk_exists(db, Provider, "Provider", peering_update.provider_id)

    if peering_update.vpc_source_id is not None:
        validate_fk_exists(db, VPC, "Source VPC", peering_update.vpc_source_id)

    if peering_update.vpc_target_id is not None:
        validate_fk_exists(db, VPC, "Target VPC", peering_update.vpc_target_id)

    updated = crud_peering.update_peering(db, peering_id, peering_update)

    if not updated:
        raise HTTPException(status_code=404, detail="VPC Peering not found")

    return updated
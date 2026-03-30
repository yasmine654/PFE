from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists
from app.schemas.vpc import VPCCreate, VPCResponse, VPCUpdate
from app.crud import vpc as crud_vpc
from app.models.vpc import VPC
from app.models.tenant import Tenant
from app.models.account import Account
from app.models.provider import Provider
from app.models.region import Region

router = APIRouter(prefix="/vpcs", tags=["VPCs"])


# ✅ CREATE
@router.post("/", response_model=VPCResponse)
def create_vpc(vpc: VPCCreate, db: Session = Depends(get_db)):

    # 🔍 Validation des parents
    validate_fk_exists(db, Tenant, "Tenant", vpc.tenant_id)
    validate_fk_exists(db, Provider, "Provider", vpc.provider_id)
    validate_fk_exists(db, Region, "Region", vpc.region_id)
    validate_fk_exists(db, Account, "Account", vpc.account_id)
    return crud_vpc.create_vpc(db, vpc)


# ✅ GET ALL
@router.get("/", response_model=list[VPCResponse])
def read_vpcs(db: Session = Depends(get_db)):
    return crud_vpc.get_vpcs(db)


# ✅ GET ONE
@router.get("/{vpc_id}", response_model=VPCResponse)
def read_vpc(vpc_id: int, db: Session = Depends(get_db)):
    vpc = crud_vpc.get_vpc(db, vpc_id)
    if not vpc:
        raise HTTPException(status_code=404, detail="VPC not found")
    return vpc


# 🔒 DELETE NORMAL
@router.delete("/{vpc_id}")
def delete_vpc(vpc_id: int, db: Session = Depends(get_db)):

    vpc = db.query(VPC).filter(
        VPC.vpc_id == vpc_id
    ).first()

    if not vpc:
        raise HTTPException(status_code=404, detail="VPC not found")

    if (
        vpc.subnets
        or vpc.vms
        or vpc.nat_gateways
        or vpc.load_balancers
        or vpc.vpn_gateways
        or vpc.wafs
        or vpc.peerings_source
        or vpc.peerings_target
    ):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete VPC with existing dependencies. Use /force."
        )

    db.delete(vpc)
    db.commit()

    return {"message": "VPC deleted"}


# 💣 DELETE FORCÉ (cascade ORM)
@router.delete("/{vpc_id}/force")
def force_delete_vpc(vpc_id: int, db: Session = Depends(get_db)):

    vpc = db.query(VPC).filter(
        VPC.vpc_id == vpc_id
    ).first()

    if not vpc:
        raise HTTPException(status_code=404, detail="VPC not found")

    db.delete(vpc)
    db.commit()

    return {"message": "VPC force deleted"}


# ✅ UPDATE
@router.put("/{vpc_id}", response_model=VPCResponse)
def update_vpc(vpc_id: int, vpc_update: VPCUpdate, db: Session = Depends(get_db)):

    # Vérifier parents si modifiés
    if vpc_update.tenant_id is not None:
        validate_fk_exists(db, Tenant, "Tenant", vpc_update.tenant_id)
    
    if vpc_update.account_id is not None:
        validate_fk_exists(db, Account, "Account", vpc_update.account_id)

    if vpc_update.provider_id is not None:
        validate_fk_exists(db, Provider, "Provider", vpc_update.provider_id)

    if vpc_update.region_id is not None:
        validate_fk_exists(db, Region, "Region", vpc_update.region_id)

    updated = crud_vpc.update_vpc(db, vpc_id, vpc_update)

    if not updated:
        raise HTTPException(status_code=404, detail="VPC not found")

    return updated
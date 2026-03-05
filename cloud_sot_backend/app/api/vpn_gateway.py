from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.vpn_gateway import (
    VPNGatewayCreate,
    VPNGatewayResponse,
    VPNGatewayUpdate
)

from app.crud import vpn_gateway as crud_vpn

from app.models.vpn_gateway import VPNGateway
from app.models.tenant import Tenant
from app.models.provider import Provider
from app.models.vpc import VPC
from app.models.subnet import Subnet

router = APIRouter(prefix="/vpn_gateways", tags=["VPN Gateways"])


# CREATE
@router.post("/", response_model=VPNGatewayResponse)
def create_vpn_gateway(vpn: VPNGatewayCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, Tenant, "Tenant", vpn.tenant_id)
    validate_fk_exists(db, Provider, "Provider", vpn.provider_id)
    validate_fk_exists(db, VPC, "VPC", vpn.vpc_id)
    validate_fk_exists(db, Subnet, "Subnet", vpn.subnet_id)

    return crud_vpn.create_vpn_gateway(db, vpn)


# GET ALL
@router.get("/", response_model=list[VPNGatewayResponse])
def read_vpn_gateways(db: Session = Depends(get_db)):

    return crud_vpn.get_vpn_gateways(db)


# GET ONE
@router.get("/{vpn_id}", response_model=VPNGatewayResponse)
def read_vpn_gateway(vpn_id: int, db: Session = Depends(get_db)):

    vpn = crud_vpn.get_vpn_gateway(db, vpn_id)

    if not vpn:
        raise HTTPException(status_code=404, detail="VPN Gateway not found")

    return vpn


# DELETE NORMAL
@router.delete("/{vpn_id}")
def delete_vpn_gateway(vpn_id: int, db: Session = Depends(get_db)):

    deleted = crud_vpn.delete_vpn_gateway(db, vpn_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="VPN Gateway not found")

    return {"message": "VPN Gateway deleted"}


# DELETE FORCE
@router.delete("/{vpn_id}/force")
def force_delete_vpn_gateway(vpn_id: int, db: Session = Depends(get_db)):

    deleted = crud_vpn.delete_vpn_gateway(db, vpn_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="VPN Gateway not found")

    return {"message": "VPN Gateway force deleted"}


# UPDATE
@router.put("/{vpn_id}", response_model=VPNGatewayResponse)
def update_vpn_gateway(vpn_id: int, vpn_update: VPNGatewayUpdate, db: Session = Depends(get_db)):

    if vpn_update.tenant_id is not None:
        validate_fk_exists(db, Tenant, "Tenant", vpn_update.tenant_id)

    if vpn_update.provider_id is not None:
        validate_fk_exists(db, Provider, "Provider", vpn_update.provider_id)

    if vpn_update.vpc_id is not None:
        validate_fk_exists(db, VPC, "VPC", vpn_update.vpc_id)

    if vpn_update.subnet_id is not None:
        validate_fk_exists(db, Subnet, "Subnet", vpn_update.subnet_id)

    updated = crud_vpn.update_vpn_gateway(db, vpn_id, vpn_update)

    if not updated:
        raise HTTPException(status_code=404, detail="VPN Gateway not found")

    return updated
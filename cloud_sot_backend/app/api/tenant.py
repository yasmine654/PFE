from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.crud import tenant as crud_tenant
from app.models.tenant import Tenant

router = APIRouter(prefix="/tenants", tags=["Tenants"])


# ✅ CREATE
@router.post("/", response_model=TenantResponse)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    return crud_tenant.create_tenant(db, tenant)


# ✅ GET ALL
@router.get("/", response_model=list[TenantResponse])
def read_tenants(db: Session = Depends(get_db)):
    return crud_tenant.get_tenants(db)


# ✅ GET ONE
@router.get("/{tenant_id}", response_model=TenantResponse)
def read_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = crud_tenant.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


# 🔒 DELETE NORMAL (bloqué si dépendances)
@router.delete("/{tenant_id}")
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):

    tenant_obj = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id
    ).first()

    if not tenant_obj:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # 🔒 Vérification via ORM
    if (
        tenant_obj.accounts
        or tenant_obj.vpcs
        or tenant_obj.vms
        or tenant_obj.vpn_gateways
        
        or tenant_obj.vpc_peerings
    ):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete tenant with existing dependencies. Use /force."
        )

    db.delete(tenant_obj)
    db.commit()

    return {"message": "Tenant deleted"}


# 💣 DELETE FORCÉ (ORM cascade supprime toute la hiérarchie)
@router.delete("/{tenant_id}/force")
def force_delete_tenant(tenant_id: int, db: Session = Depends(get_db)):

    tenant_obj = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id
    ).first()

    if not tenant_obj:
        raise HTTPException(status_code=404, detail="Tenant not found")

    db.delete(tenant_obj)   # 🔥 cascade ORM fait tout
    db.commit()

    return {"message": "Tenant force deleted"}


# ✅ UPDATE
@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(tenant_id: int, tenant: TenantUpdate, db: Session = Depends(get_db)):
    updated_tenant = crud_tenant.update_tenant(db, tenant_id, tenant)

    if not updated_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return updated_tenant
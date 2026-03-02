from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.crud import tenant as crud_tenant
from app.models.tenant import Tenant
from app.models.account import Account

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

    if tenant_obj.accounts:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete tenant with existing accounts. Use /force endpoint."
        )

    db.delete(tenant_obj)
    db.commit()

    return {"message": "Tenant deleted"}


# 💣 DELETE FORCÉ
@router.delete("/{tenant_id}/force")
def force_delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant_obj = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id
    ).first()

    if not tenant_obj:
        raise HTTPException(status_code=404, detail="Tenant not found")

    try:
        # 🔥 supprimer les accounts liés
        db.query(Account).filter(
            Account.tenant_id == tenant_id
        ).delete()

        db.delete(tenant_obj)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Tenant still has other dependencies."
        )

    return {"message": "Tenant force deleted"}


# ✅ UPDATE
@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(tenant_id: int, tenant: TenantUpdate, db: Session = Depends(get_db)):
    updated_tenant = crud_tenant.update_tenant(db, tenant_id, tenant)

    if not updated_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return updated_tenant
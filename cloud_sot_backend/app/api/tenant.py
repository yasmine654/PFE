from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.crud import tenant as crud_tenant

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.post("/", response_model=TenantResponse)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    return crud_tenant.create_tenant(db, tenant)

@router.get("/", response_model=list[TenantResponse])
def read_tenants(db: Session = Depends(get_db)):
    return crud_tenant.get_tenants(db)

@router.get("/{tenant_id}", response_model=TenantResponse)
def read_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = crud_tenant.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.delete("/{tenant_id}")
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = crud_tenant.delete_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant deleted"}

@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(tenant_id: int, tenant: TenantUpdate, db: Session = Depends(get_db)):
    updated_tenant = crud_tenant.update_tenant(db, tenant_id, tenant)
    
    if not updated_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return updated_tenant
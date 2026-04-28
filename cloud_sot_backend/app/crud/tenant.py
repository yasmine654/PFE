from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate

def create_tenant(db: Session, tenant: TenantCreate):
    db_tenant = Tenant(**tenant.model_dump())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def get_tenants(db: Session):
    return db.query(Tenant).all()

def get_tenant(db: Session, tenant_id: int):
    return db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()

def delete_tenant(db: Session, tenant_id: int):
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if tenant:
        db.delete(tenant)
        db.commit()
    return tenant

def update_tenant(db: Session, tenant_id: int, tenant_update):
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    
    if not tenant:
        return None

    for key, value in tenant_update.model_dump(exclude_unset=True).items():
        setattr(tenant, key, value)

    db.commit()
    db.refresh(tenant)
    return tenant
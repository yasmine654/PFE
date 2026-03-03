from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.provider import ProviderCreate, ProviderResponse, ProviderUpdate
from app.crud import provider as crud_provider
from app.models.provider import Provider

router = APIRouter(prefix="/providers", tags=["Providers"])


# ✅ CREATE
@router.post("/", response_model=ProviderResponse)
def create_provider(provider: ProviderCreate, db: Session = Depends(get_db)):
    return crud_provider.create_provider(db, provider)


# ✅ GET ALL
@router.get("/", response_model=list[ProviderResponse])
def read_providers(db: Session = Depends(get_db)):
    return crud_provider.get_providers(db)


# ✅ GET ONE
@router.get("/{provider_id}", response_model=ProviderResponse)
def read_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = crud_provider.get_provider(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


# 🔒 DELETE NORMAL (bloqué si dépendances)
@router.delete("/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db)):

    provider_obj = db.query(Provider).filter(
        Provider.provider_id == provider_id
    ).first()

    if not provider_obj:
        raise HTTPException(status_code=404, detail="Provider not found")

    # 🔒 Vérification via ORM (relationships)
    if (
        provider_obj.accounts
        or provider_obj.regions
        or provider_obj.vpcs
        or provider_obj.vms
        or provider_obj.vpn_gateways
        or provider_obj.elastic_ips
        or provider_obj.vpc_peerings
    ):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete provider with existing dependencies. Use /force."
        )

    db.delete(provider_obj)
    db.commit()

    return {"message": "Provider deleted"}


# 💣 DELETE FORCÉ (ORM cascade supprime toute la hiérarchie)
@router.delete("/{provider_id}/force")
def force_delete_provider(provider_id: int, db: Session = Depends(get_db)):

    provider_obj = db.query(Provider).filter(
        Provider.provider_id == provider_id
    ).first()

    if not provider_obj:
        raise HTTPException(status_code=404, detail="Provider not found")

    db.delete(provider_obj)   # 🔥 cascade ORM fait tout
    db.commit()

    return {"message": "Provider force deleted"}


# ✅ UPDATE
@router.put("/{provider_id}", response_model=ProviderResponse)
def update_provider(provider_id: int, provider: ProviderUpdate, db: Session = Depends(get_db)):
    updated = crud_provider.update_provider(db, provider_id, provider)
    if not updated:
        raise HTTPException(status_code=404, detail="Provider not found")
    return updated
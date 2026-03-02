from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.schemas.provider import ProviderCreate, ProviderResponse, ProviderUpdate
from app.crud import provider as crud_provider
from app.models.provider import Provider
from app.models.account import Account

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

    if provider_obj.accounts:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete provider with existing accounts. Use /force endpoint."
        )

    db.delete(provider_obj)
    db.commit()

    return {"message": "Provider deleted"}


# 💣 DELETE FORCÉ (supprime les dépendances)
@router.delete("/{provider_id}/force")
def force_delete_provider(provider_id: int, db: Session = Depends(get_db)):
    provider_obj = db.query(Provider).filter(
        Provider.provider_id == provider_id
    ).first()

    if not provider_obj:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        # 🔥 suppression des accounts liés
        db.query(Account).filter(
            Account.provider_id == provider_id
        ).delete()

        db.delete(provider_obj)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Provider still has other dependencies."
        )

    return {"message": "Provider force deleted"}


# ✅ UPDATE
@router.put("/{provider_id}", response_model=ProviderResponse)
def update_provider(provider_id: int, provider: ProviderUpdate, db: Session = Depends(get_db)):
    updated = crud_provider.update_provider(db, provider_id, provider)
    if not updated:
        raise HTTPException(status_code=404, detail="Provider not found")
    return updated
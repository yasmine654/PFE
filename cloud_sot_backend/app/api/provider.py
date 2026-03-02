from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.provider import ProviderCreate, ProviderResponse, ProviderUpdate
from app.crud import provider as crud_provider

router = APIRouter(prefix="/providers", tags=["Providers"])

@router.post("/", response_model=ProviderResponse)
def create_provider(provider: ProviderCreate, db: Session = Depends(get_db)):
    return crud_provider.create_provider(db, provider)

@router.get("/", response_model=list[ProviderResponse])
def read_providers(db: Session = Depends(get_db)):
    return crud_provider.get_providers(db)

@router.get("/{provider_id}", response_model=ProviderResponse)
def read_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = crud_provider.get_provider(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.delete("/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    deleted = crud_provider.delete_provider(db, provider_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Provider not found")

    return {"message": "Provider deleted"}

@router.put("/{provider_id}", response_model=ProviderResponse)
def update_provider(provider_id: int, provider: ProviderUpdate, db: Session = Depends(get_db)):
    updated = crud_provider.update_provider(db, provider_id, provider)
    if not updated:
        raise HTTPException(status_code=404, detail="Provider not found")
    return updated
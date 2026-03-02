from sqlalchemy.orm import Session
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate

def create_provider(db: Session, provider: ProviderCreate):
    db_provider = Provider(**provider.dict())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def get_providers(db: Session):
    return db.query(Provider).all()

def get_provider(db: Session, provider_id: int):
    return db.query(Provider).filter(
        Provider.provider_id == provider_id
    ).first()

def delete_provider(db: Session, provider_id: int):
    provider = db.query(Provider).filter(
        Provider.provider_id == provider_id
    ).first()

    if not provider:
        return False

    db.delete(provider)
    db.commit()
    return True

def update_provider(db: Session, provider_id: int, provider_update):
    provider = db.query(Provider).filter(
        Provider.provider_id == provider_id
    ).first()

    if not provider:
        return None

    for key, value in provider_update.dict(exclude_unset=True).items():
        setattr(provider, key, value)

    db.commit()
    db.refresh(provider)
    return provider
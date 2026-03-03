from fastapi import HTTPException
from sqlalchemy.orm import Session


def validate_fk_exists(db: Session, model, field_name: str, value: int):
    """
    Vérifie qu'une clé étrangère existe.
    model: modèle SQLAlchemy (ex: Provider)
    field_name: nom du champ pour message d'erreur (ex: "Provider")
    value: id à vérifier
    """
    obj = db.query(model).filter(
        getattr(model, list(model.__table__.primary_key.columns)[0].name) == value
    ).first()

    if not obj:
        raise HTTPException(
            status_code=404,
            detail=f"{field_name} with id {value} does not exist"
        )

    return obj
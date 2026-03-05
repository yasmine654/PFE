from sqlalchemy.orm import Session
from app.models.waf import WAF


def create_waf(db: Session, waf):

    db_waf = WAF(**waf.model_dump())

    db.add(db_waf)
    db.commit()
    db.refresh(db_waf)

    return db_waf


def get_wafs(db: Session):

    return db.query(WAF).all()


def get_waf(db: Session, waf_id: int):

    return db.query(WAF).filter(
        WAF.waf_id == waf_id
    ).first()


def update_waf(db: Session, waf_id: int, waf_update):

    waf = get_waf(db, waf_id)

    if not waf:
        return None

    update_data = waf_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(waf, key, value)

    db.commit()
    db.refresh(waf)

    return waf


def delete_waf(db: Session, waf_id: int):

    waf = get_waf(db, waf_id)

    if not waf:
        return None

    db.delete(waf)
    db.commit()

    return waf
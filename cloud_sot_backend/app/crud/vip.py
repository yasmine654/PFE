from sqlalchemy.orm import Session
from app.models.vip import VIP


def create_vip(db: Session, vip):

    db_vip = VIP(**vip.model_dump())
    db.add(db_vip)
    db.commit()
    db.refresh(db_vip)

    return db_vip


def get_vips(db: Session):

    return db.query(VIP).all()


def get_vip(db: Session, vip_id: int):

    return db.query(VIP).filter(VIP.vip_id == vip_id).first()


def update_vip(db: Session, vip_id: int, vip_update):

    vip = db.query(VIP).filter(VIP.vip_id == vip_id).first()

    if not vip:
        return None

    update_data = vip_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(vip, key, value)

    db.commit()
    db.refresh(vip)

    return vip
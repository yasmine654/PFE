from sqlalchemy.orm import Session
from app.models.vpc_peering import VPCPeering


def create_vpc_peering(db: Session, peering):
    db_peering = VPCPeering(**peering.model_dump())
    db.add(db_peering)
    db.commit()
    db.refresh(db_peering)
    return db_peering


def get_peerings(db: Session):
    return db.query(VPCPeering).all()


def get_peering(db: Session, peering_id: int):
    return db.query(VPCPeering).filter(
        VPCPeering.peering_id == peering_id
    ).first()


def update_peering(db: Session, peering_id: int, peering_update):

    peering = get_peering(db, peering_id)

    if not peering:
        return None

    update_data = peering_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(peering, key, value)

    db.commit()
    db.refresh(peering)

    return peering
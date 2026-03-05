from sqlalchemy.orm import Session
from app.models.nat_gateway import NATGateway


def create_nat_gateway(db: Session, nat):

    db_nat = NATGateway(**nat.model_dump())

    db.add(db_nat)
    db.commit()
    db.refresh(db_nat)

    return db_nat


def get_nat_gateways(db: Session):

    return db.query(NATGateway).all()


def get_nat_gateway(db: Session, nat_id: int):

    return db.query(NATGateway).filter(
        NATGateway.nat_id == nat_id
    ).first()


def update_nat_gateway(db: Session, nat_id: int, nat_update):

    nat = get_nat_gateway(db, nat_id)

    if not nat:
        return None

    update_data = nat_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(nat, key, value)

    db.commit()
    db.refresh(nat)

    return nat
from sqlalchemy.orm import Session
from app.models.vpn_gateway import VPNGateway


def create_vpn_gateway(db: Session, vpn):

    db_vpn = VPNGateway(**vpn.model_dump())

    db.add(db_vpn)
    db.commit()
    db.refresh(db_vpn)

    return db_vpn


def get_vpn_gateways(db: Session):

    return db.query(VPNGateway).all()


def get_vpn_gateway(db: Session, vpn_id: int):

    return db.query(VPNGateway).filter(
        VPNGateway.vpn_id == vpn_id
    ).first()


def update_vpn_gateway(db: Session, vpn_id: int, vpn_update):

    vpn = get_vpn_gateway(db, vpn_id)

    if not vpn:
        return None

    update_data = vpn_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(vpn, key, value)

    db.commit()
    db.refresh(vpn)

    return vpn


def delete_vpn_gateway(db: Session, vpn_id: int):

    vpn = get_vpn_gateway(db, vpn_id)

    if not vpn:
        return None

    db.delete(vpn)
    db.commit()

    return vpn
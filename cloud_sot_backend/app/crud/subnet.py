from sqlalchemy.orm import Session
from app.models.subnet import Subnet


def create_subnet(db: Session, subnet):
    db_subnet = Subnet(**subnet.model_dump())
    db.add(db_subnet)
    db.commit()
    db.refresh(db_subnet)
    return db_subnet


def get_subnets(db: Session):
    return db.query(Subnet).all()


def get_subnet(db: Session, subnet_id: int):
    return db.query(Subnet).filter(
        Subnet.subnet_id == subnet_id
    ).first()


def update_subnet(db: Session, subnet_id: int, subnet_update):
    subnet = get_subnet(db, subnet_id)
    if not subnet:
        return None

    update_data = subnet_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(subnet, key, value)

    db.commit()
    db.refresh(subnet)
    return subnet
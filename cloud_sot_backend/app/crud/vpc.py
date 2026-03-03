from sqlalchemy.orm import Session
from app.models.vpc import VPC


def create_vpc(db: Session, vpc):
    db_vpc = VPC(**vpc.model_dump())
    db.add(db_vpc)
    db.commit()
    db.refresh(db_vpc)
    return db_vpc


def get_vpcs(db: Session):
    return db.query(VPC).all()


def get_vpc(db: Session, vpc_id: int):
    return db.query(VPC).filter(
        VPC.vpc_id == vpc_id
    ).first()


def update_vpc(db: Session, vpc_id: int, vpc_update):
    vpc = get_vpc(db, vpc_id)
    if not vpc:
        return None

    update_data = vpc_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(vpc, key, value)

    db.commit()
    db.refresh(vpc)
    return vpc
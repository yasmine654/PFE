from sqlalchemy.orm import Session
from app.models.availability_zone import AvailabilityZone


def create_availability_zone(db: Session, az):
    db_az = AvailabilityZone(**az.model_dump())
    db.add(db_az)
    db.commit()
    db.refresh(db_az)
    return db_az


def get_availability_zones(db: Session):
    return db.query(AvailabilityZone).all()


def get_availability_zone(db: Session, az_id: int):
    return db.query(AvailabilityZone).filter(
        AvailabilityZone.az_id == az_id
    ).first()


def update_availability_zone(db: Session, az_id: int, az_update):
    az = get_availability_zone(db, az_id)
    if not az:
        return None

    update_data = az_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(az, key, value)

    db.commit()
    db.refresh(az)
    return az
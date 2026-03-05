from sqlalchemy.orm import Session
from app.models.volume import Volume


def create_volume(db: Session, volume):

    db_volume = Volume(**volume.model_dump())

    db.add(db_volume)
    db.commit()
    db.refresh(db_volume)

    return db_volume


def get_volumes(db: Session):

    return db.query(Volume).all()


def get_volume(db: Session, volume_id: int):

    return db.query(Volume).filter(
        Volume.volume_id == volume_id
    ).first()


def update_volume(db: Session, volume_id: int, volume_update):

    volume = get_volume(db, volume_id)

    if not volume:
        return None

    update_data = volume_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(volume, key, value)

    db.commit()
    db.refresh(volume)

    return volume


def delete_volume(db: Session, volume_id: int):

    volume = get_volume(db, volume_id)

    if not volume:
        return None

    db.delete(volume)
    db.commit()

    return volume
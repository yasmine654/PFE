from sqlalchemy.orm import Session
from app.models.region import Region

def create_region(db: Session, region):
    db_region = Region(**region.model_dump())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region

def get_regions(db: Session):
    return db.query(Region).all()

def get_region(db: Session, region_id: int):
    return db.query(Region).filter(
        Region.region_id == region_id
    ).first()

def update_region(db: Session, region_id: int, region_update):
    region = db.query(Region).filter(
        Region.region_id == region_id
    ).first()

    if not region:
        return None

    update_data = region_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(region, key, value)

    db.commit()
    db.refresh(region)
    return region
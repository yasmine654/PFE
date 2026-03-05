from sqlalchemy.orm import Session
from app.models.security_group import SecurityGroup


def create_security_group(db: Session, sg):

    db_sg = SecurityGroup(**sg.model_dump())

    db.add(db_sg)
    db.commit()
    db.refresh(db_sg)

    return db_sg


def get_security_groups(db: Session):

    return db.query(SecurityGroup).all()


def get_security_group(db: Session, sg_id: int):

    return db.query(SecurityGroup).filter(
        SecurityGroup.sg_id == sg_id
    ).first()


def update_security_group(db: Session, sg_id: int, sg_update):

    sg = get_security_group(db, sg_id)

    if not sg:
        return None

    update_data = sg_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(sg, key, value)

    db.commit()
    db.refresh(sg)

    return sg


def delete_security_group(db: Session, sg_id: int):

    sg = get_security_group(db, sg_id)

    if not sg:
        return None

    db.delete(sg)
    db.commit()

    return sg
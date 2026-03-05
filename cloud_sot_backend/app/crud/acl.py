from sqlalchemy.orm import Session
from app.models.acl import ACL


def create_acl(db: Session, acl):

    db_acl = ACL(**acl.model_dump())

    db.add(db_acl)
    db.commit()
    db.refresh(db_acl)

    return db_acl


def get_acls(db: Session):

    return db.query(ACL).all()


def get_acl(db: Session, acl_id: int):

    return db.query(ACL).filter(
        ACL.acl_id == acl_id
    ).first()


def update_acl(db: Session, acl_id: int, acl_update):

    acl = get_acl(db, acl_id)

    if not acl:
        return None

    update_data = acl_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(acl, key, value)

    db.commit()
    db.refresh(acl)

    return acl


def delete_acl(db: Session, acl_id: int):

    acl = get_acl(db, acl_id)

    if not acl:
        return None

    db.delete(acl)
    db.commit()

    return acl
from sqlalchemy.orm import Session
from app.models.elastic_ip import ElasticIP


def create_elastic_ip(db: Session, elastic_ip):

    db_eip = ElasticIP(**elastic_ip.model_dump())

    db.add(db_eip)
    db.commit()
    db.refresh(db_eip)

    return db_eip


def get_elastic_ips(db: Session):

    return db.query(ElasticIP).all()


def get_elastic_ip(db: Session, elastic_ip_id: int):

    return db.query(ElasticIP).filter(
        ElasticIP.elastic_ip_id == elastic_ip_id
    ).first()


def update_elastic_ip(db: Session, elastic_ip_id: int, elastic_ip_update):

    eip = get_elastic_ip(db, elastic_ip_id)

    if not eip:
        return None

    update_data = elastic_ip_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(eip, key, value)

    db.commit()
    db.refresh(eip)

    return eip
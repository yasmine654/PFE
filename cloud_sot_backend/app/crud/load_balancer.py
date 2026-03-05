from sqlalchemy.orm import Session
from app.models.load_balancer import LoadBalancer


def create_load_balancer(db: Session, lb):

    db_lb = LoadBalancer(**lb.model_dump())

    db.add(db_lb)
    db.commit()
    db.refresh(db_lb)

    return db_lb


def get_load_balancers(db: Session):

    return db.query(LoadBalancer).all()


def get_load_balancer(db: Session, lb_id: int):

    return db.query(LoadBalancer).filter(
        LoadBalancer.lb_id == lb_id
    ).first()


def update_load_balancer(db: Session, lb_id: int, lb_update):

    lb = get_load_balancer(db, lb_id)

    if not lb:
        return None

    update_data = lb_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(lb, key, value)

    db.commit()
    db.refresh(lb)

    return lb
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.load_balancer import (
    LoadBalancerCreate,
    LoadBalancerResponse,
    LoadBalancerUpdate
)

from app.crud import load_balancer as crud_lb

from app.models.load_balancer import LoadBalancer
from app.models.vpc import VPC
from app.models.subnet import Subnet

router = APIRouter(prefix="/load_balancers", tags=["Load Balancers"])


# CREATE
@router.post("/", response_model=LoadBalancerResponse)
def create_load_balancer(lb: LoadBalancerCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, VPC, "VPC", lb.vpc_id)
    validate_fk_exists(db, Subnet, "Subnet", lb.subnet_id)

    return crud_lb.create_load_balancer(db, lb)


# GET ALL
@router.get("/", response_model=list[LoadBalancerResponse])
def read_load_balancers(db: Session = Depends(get_db)):

    return crud_lb.get_load_balancers(db)


# GET ONE
@router.get("/{lb_id}", response_model=LoadBalancerResponse)
def read_load_balancer(lb_id: int, db: Session = Depends(get_db)):

    lb = crud_lb.get_load_balancer(db, lb_id)

    if not lb:
        raise HTTPException(status_code=404, detail="Load Balancer not found")

    return lb


@router.delete("/{lb_id}")
def delete_load_balancer(lb_id: int, db: Session = Depends(get_db)):

    lb = db.query(LoadBalancer).filter(
        LoadBalancer.lb_id == lb_id
    ).first()

    if not lb:
        raise HTTPException(status_code=404, detail="Load Balancer not found")

    # 🔒 check dépendances (VIP)
    if lb.vips:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete load balancer with existing dependencies. Use /force."
        )

    db.delete(lb)
    db.commit()

    return {"message": "Load Balancer deleted"}


# DELETE FORCE
@router.delete("/{lb_id}/force")
def force_delete_load_balancer(lb_id: int, db: Session = Depends(get_db)):

    lb = db.query(LoadBalancer).filter(
        LoadBalancer.lb_id == lb_id
    ).first()

    if not lb:
        raise HTTPException(status_code=404, detail="Load Balancer not found")

    db.delete(lb)
    db.commit()

    return {"message": "Load Balancer force deleted"}


# UPDATE
@router.put("/{lb_id}", response_model=LoadBalancerResponse)
def update_load_balancer(lb_id: int, lb_update: LoadBalancerUpdate, db: Session = Depends(get_db)):

    if lb_update.vpc_id is not None:
        validate_fk_exists(db, VPC, "VPC", lb_update.vpc_id)

    if lb_update.subnet_id is not None:
        validate_fk_exists(db, Subnet, "Subnet", lb_update.subnet_id)

    updated = crud_lb.update_load_balancer(db, lb_id, lb_update)

    if not updated:
        raise HTTPException(status_code=404, detail="Load Balancer not found")

    return updated
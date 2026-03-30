from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.vip import VIPCreate, VIPResponse, VIPUpdate
from app.crud import vip as crud_vip

from app.models.vip import VIP
from app.models.subnet import Subnet
from app.models.load_balancer import LoadBalancer

router = APIRouter(prefix="/vips", tags=["VIP"])


@router.post("/", response_model=VIPResponse)
def create_vip(vip: VIPCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, Subnet, "Subnet", vip.subnet_id)
    validate_fk_exists(db, LoadBalancer, "LoadBalancer", vip.loadbalancer_id)

    return crud_vip.create_vip(db, vip)


@router.get("/", response_model=list[VIPResponse])
def read_vips(db: Session = Depends(get_db)):

    return crud_vip.get_vips(db)


@router.get("/{vip_id}", response_model=VIPResponse)
def read_vip(vip_id: int, db: Session = Depends(get_db)):

    vip = crud_vip.get_vip(db, vip_id)

    if not vip:
        raise HTTPException(status_code=404, detail="VIP not found")

    return vip


@router.put("/{vip_id}", response_model=VIPResponse)
def update_vip(vip_id: int, vip_update: VIPUpdate, db: Session = Depends(get_db)):

    updated = crud_vip.update_vip(db, vip_id, vip_update)

    if not updated:
        raise HTTPException(status_code=404, detail="VIP not found")

    return updated


@router.delete("/{vip_id}")
def delete_vip(vip_id: int, db: Session = Depends(get_db)):

    vip = db.query(VIP).filter(VIP.vip_id == vip_id).first()

    if not vip:
        raise HTTPException(status_code=404, detail="VIP not found")

    db.delete(vip)
    db.commit()

    return {"message": "VIP deleted"}
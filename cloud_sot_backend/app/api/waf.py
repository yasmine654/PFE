from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.waf import (
    WAFCreate,
    WAFResponse,
    WAFUpdate
)

from app.crud import waf as crud_waf

from app.models.waf import WAF
from app.models.vpc import VPC
from app.models.subnet import Subnet
from app.models.elastic_ip import ElasticIP

router = APIRouter(prefix="/wafs", tags=["WAFs"])


# CREATE
@router.post("/", response_model=WAFResponse)
def create_waf(waf: WAFCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, VPC, "VPC", waf.vpc_id)
    validate_fk_exists(db, Subnet, "Subnet", waf.subnet_id)

    if waf.elastic_ip_id:
        validate_fk_exists(db, ElasticIP, "Elastic IP", waf.elastic_ip_id)

    return crud_waf.create_waf(db, waf)


# GET ALL
@router.get("/", response_model=list[WAFResponse])
def read_wafs(db: Session = Depends(get_db)):

    return crud_waf.get_wafs(db)


# GET ONE
@router.get("/{waf_id}", response_model=WAFResponse)
def read_waf(waf_id: int, db: Session = Depends(get_db)):

    waf = crud_waf.get_waf(db, waf_id)

    if not waf:
        raise HTTPException(status_code=404, detail="WAF not found")

    return waf


# DELETE NORMAL
@router.delete("/{waf_id}")
def delete_waf(waf_id: int, db: Session = Depends(get_db)):

    deleted = crud_waf.delete_waf(db, waf_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="WAF not found")

    return {"message": "WAF deleted"}


# DELETE FORCE
@router.delete("/{waf_id}/force")
def force_delete_waf(waf_id: int, db: Session = Depends(get_db)):

    deleted = crud_waf.delete_waf(db, waf_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="WAF not found")

    return {"message": "WAF force deleted"}


# UPDATE
@router.put("/{waf_id}", response_model=WAFResponse)
def update_waf(waf_id: int, waf_update: WAFUpdate, db: Session = Depends(get_db)):

    if waf_update.vpc_id is not None:
        validate_fk_exists(db, VPC, "VPC", waf_update.vpc_id)

    if waf_update.subnet_id is not None:
        validate_fk_exists(db, Subnet, "Subnet", waf_update.subnet_id)

    if waf_update.elastic_ip_id is not None:
        validate_fk_exists(db, ElasticIP, "Elastic IP", waf_update.elastic_ip_id)

    updated = crud_waf.update_waf(db, waf_id, waf_update)

    if not updated:
        raise HTTPException(status_code=404, detail="WAF not found")

    return updated
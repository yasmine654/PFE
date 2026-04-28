from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.elastic_ip import (
    ElasticIPCreate,
    ElasticIPResponse,
    ElasticIPUpdate
)

from app.crud import elastic_ip as crud_eip
from app.models.elastic_ip import ElasticIP
from app.models.provider import Provider
from app.models.region import Region

router = APIRouter(prefix="/elastic_ips", tags=["Elastic IPs"])


def _to_response(eip: ElasticIP) -> ElasticIPResponse:
    return ElasticIPResponse(
        elastic_ip_id=eip.elastic_ip_id,
        ip=eip.ip,
        provider_id=eip.provider_id,
        region_id=eip.region_id,
        is_attached=eip.vm is not None,
        vm_id=eip.vm.vm_id if eip.vm else None
    )

@router.post("/", response_model=ElasticIPResponse)
def create_elastic_ip(eip: ElasticIPCreate, db: Session = Depends(get_db)):
    validate_fk_exists(db, Provider, "Provider", eip.provider_id)
    validate_fk_exists(db, Region, "Region", eip.region_id)
    created = crud_eip.create_elastic_ip(db, eip)
    return _to_response(created)


@router.get("/", response_model=list[ElasticIPResponse])
def read_elastic_ips(db: Session = Depends(get_db)):
    return [_to_response(e) for e in crud_eip.get_elastic_ips(db)]


@router.get("/{elastic_ip_id}", response_model=ElasticIPResponse)
def read_elastic_ip(elastic_ip_id: int, db: Session = Depends(get_db)):
    eip = crud_eip.get_elastic_ip(db, elastic_ip_id)
    if not eip:
        raise HTTPException(status_code=404, detail="Elastic IP not found")
    return _to_response(eip)


@router.delete("/{elastic_ip_id}")
def delete_elastic_ip(elastic_ip_id: int, db: Session = Depends(get_db)):
    eip = db.query(ElasticIP).filter(
        ElasticIP.elastic_ip_id == elastic_ip_id
    ).first()
    if not eip:
        raise HTTPException(status_code=404, detail="Elastic IP not found")
    if eip.vm:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete EIP attached to a VM. Detach first or use /force."
        )
    db.delete(eip)
    db.commit()
    return {"message": "Elastic IP deleted"}


@router.delete("/{elastic_ip_id}/force")
def force_delete_elastic_ip(elastic_ip_id: int, db: Session = Depends(get_db)):
    eip = db.query(ElasticIP).filter(
        ElasticIP.elastic_ip_id == elastic_ip_id
    ).first()
    if not eip:
        raise HTTPException(status_code=404, detail="Elastic IP not found")
    db.delete(eip)
    db.commit()
    return {"message": "Elastic IP force deleted"}


@router.put("/{elastic_ip_id}", response_model=ElasticIPResponse)
def update_elastic_ip(elastic_ip_id: int, eip_update: ElasticIPUpdate, db: Session = Depends(get_db)):
    if eip_update.provider_id is not None:
        validate_fk_exists(db, Provider, "Provider", eip_update.provider_id)
    if eip_update.region_id is not None:
        validate_fk_exists(db, Region, "Region", eip_update.region_id)
    updated = crud_eip.update_elastic_ip(db, elastic_ip_id, eip_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Elastic IP not found")
    return _to_response(updated)
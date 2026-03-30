from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.validators import validate_fk_exists

from app.schemas.vm import (
    VMCreate,
    VMResponse,
    VMUpdate
)

from app.crud import vm as crud_vm

from app.models.vm import VM
from app.models.tenant import Tenant
from app.models.provider import Provider
from app.models.region import Region
from app.models.availability_zone import AvailabilityZone
from app.models.subnet import Subnet
from app.models.elastic_ip import ElasticIP

router = APIRouter(prefix="/vms", tags=["VMs"])


# CREATE
@router.post("/", response_model=VMResponse)
def create_vm(vm: VMCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, Tenant, "Tenant", vm.tenant_id)
    validate_fk_exists(db, Provider, "Provider", vm.provider_id)
    validate_fk_exists(db, Region, "Region", vm.region_id)
    validate_fk_exists(db, AvailabilityZone, "Availability Zone", vm.az_id)
    validate_fk_exists(db, Subnet, "Subnet", vm.subnet_id)

    if vm.elastic_ip_id is not None:
        validate_fk_exists(db, ElasticIP, "Elastic IP", vm.elastic_ip_id)

    return crud_vm.create_vm(db, vm)


# GET ALL
@router.get("/", response_model=list[VMResponse])
def read_vms(db: Session = Depends(get_db)):

    return crud_vm.get_vms(db)


# GET ONE
@router.get("/{vm_id}", response_model=VMResponse)
def read_vm(vm_id: int, db: Session = Depends(get_db)):

    vm = crud_vm.get_vm(db, vm_id)

    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")

    return vm


# DELETE NORMAL
@router.delete("/{vm_id}")
def delete_vm(vm_id: int, db: Session = Depends(get_db)):

    vm = db.query(VM).filter(
        VM.vm_id == vm_id
    ).first()

    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")

    if vm.volumes or vm.security_groups:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete VM with dependencies. Use /force."
        )

    db.delete(vm)
    db.commit()

    return {"message": "VM deleted"}


# DELETE FORCE
@router.delete("/{vm_id}/force")
def force_delete_vm(vm_id: int, db: Session = Depends(get_db)):

    vm = db.query(VM).filter(
        VM.vm_id == vm_id
    ).first()

    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")

    db.delete(vm)
    db.commit()

    return {"message": "VM force deleted"}


# UPDATE
@router.put("/{vm_id}", response_model=VMResponse)
def update_vm(vm_id: int, vm_update: VMUpdate, db: Session = Depends(get_db)):

    if vm_update.tenant_id is not None:
        validate_fk_exists(db, Tenant, "Tenant", vm_update.tenant_id)

    if vm_update.provider_id is not None:
        validate_fk_exists(db, Provider, "Provider", vm_update.provider_id)

    if vm_update.region_id is not None:
        validate_fk_exists(db, Region, "Region", vm_update.region_id)

    if vm_update.az_id is not None:
        validate_fk_exists(db, AvailabilityZone, "Availability Zone", vm_update.az_id)

    if vm_update.subnet_id is not None:
        validate_fk_exists(db, Subnet, "Subnet", vm_update.subnet_id)

    if vm_update.elastic_ip_id is not None:
        validate_fk_exists(db, ElasticIP, "Elastic IP", vm_update.elastic_ip_id)

    updated = crud_vm.update_vm(db, vm_id, vm_update)

    if not updated:
        raise HTTPException(status_code=404, detail="VM not found")

    return updated
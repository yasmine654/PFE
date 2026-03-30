from pydantic import BaseModel
from typing import Optional


class VMBase(BaseModel):
    name: str

    tenant_id: int
    provider_id: int
    region_id: int
    az_id: int
    subnet_id: int
    vpc_id: int

    instance_type: Optional[str] = None
    vcpu: Optional[int] = None
    ram: Optional[int] = None

    os: Optional[str] = None
    image: Optional[str] = None

    private_ip: Optional[str] = None
    elastic_ip_id: Optional[int] = None

    state: Optional[str] = None


class VMCreate(VMBase):
    pass


class VMUpdate(BaseModel):
    name: Optional[str] = None

    tenant_id: Optional[int] = None
    provider_id: Optional[int] = None
    region_id: Optional[int] = None
    az_id: Optional[int] = None
    subnet_id: Optional[int] = None
    vpc_id: Optional[int] = None

    instance_type: Optional[str] = None
    vcpu: Optional[int] = None
    ram: Optional[int] = None

    os: Optional[str] = None
    image: Optional[str] = None

    private_ip: Optional[str] = None
    elastic_ip_id: Optional[int] = None

    state: Optional[str] = None


class VMResponse(VMBase):
    vm_id: int

    model_config = {
        "from_attributes": True
    }
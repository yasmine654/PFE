from pydantic import BaseModel
from typing import Optional


class VPCBase(BaseModel):
    tenant_id: int
    account_id: int
    provider_id: int
    region_id: int
    cidr: str
    name: Optional[str] = None
    state: Optional[str] = None


class VPCCreate(VPCBase):
    pass


class VPCUpdate(BaseModel):
    cidr: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None
    tenant_id: Optional[int] = None
    provider_id: Optional[int] = None
    region_id: Optional[int] = None
    account_id: Optional[int] = None


class VPCResponse(VPCBase):
    vpc_id: int

    model_config = {
        "from_attributes": True
    }
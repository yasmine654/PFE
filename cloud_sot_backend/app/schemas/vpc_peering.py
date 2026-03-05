from pydantic import BaseModel
from typing import Optional


class VPCPeeringBase(BaseModel):

    tenant_id: int
    provider_id: int

    vpc_source_id: int
    vpc_target_id: int

    region_source: Optional[str] = None
    region_target: Optional[str] = None


class VPCPeeringCreate(VPCPeeringBase):
    pass


class VPCPeeringUpdate(BaseModel):

    tenant_id: Optional[int] = None
    provider_id: Optional[int] = None

    vpc_source_id: Optional[int] = None
    vpc_target_id: Optional[int] = None

    region_source: Optional[str] = None
    region_target: Optional[str] = None


class VPCPeeringResponse(VPCPeeringBase):

    peering_id: int

    model_config = {
        "from_attributes": True
    }
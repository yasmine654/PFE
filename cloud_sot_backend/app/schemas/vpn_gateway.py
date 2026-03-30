from pydantic import BaseModel
from typing import Optional


class VPNGatewayBase(BaseModel):

    tenant_id: int
    provider_id: int
    vpc_id: int
    subnet_id: int

    type: str
    elastic_ip_id: Optional[int] = None


class VPNGatewayCreate(VPNGatewayBase):
    pass


class VPNGatewayUpdate(BaseModel):

    tenant_id: Optional[int] = None
    provider_id: Optional[int] = None
    vpc_id: Optional[int] = None
    subnet_id: Optional[int] = None

    type: Optional[str] = None
    elastic_ip_id: Optional[int] = None


class VPNGatewayResponse(VPNGatewayBase):

    vpn_id: int

    model_config = {
        "from_attributes": True
    }
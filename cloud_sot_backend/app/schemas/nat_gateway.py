from pydantic import BaseModel
from typing import Optional


class NATGatewayBase(BaseModel):

    vpc_id: int
    snat_rule: Optional[str] = None
    dnat_rule: Optional[str] = None


class NATGatewayCreate(NATGatewayBase):
    pass


class NATGatewayUpdate(BaseModel):

    vpc_id: Optional[int] = None
    snat_rule: Optional[str] = None
    dnat_rule: Optional[str] = None


class NATGatewayResponse(NATGatewayBase):

    nat_id: int

    model_config = {
        "from_attributes": True
    }
from pydantic import BaseModel
from typing import Optional


class LoadBalancerBase(BaseModel):

    type: str
    ip_private: str
    vpc_id: int
    subnet_id: int


class LoadBalancerCreate(LoadBalancerBase):
    pass


class LoadBalancerUpdate(BaseModel):

    type: Optional[str] = None
    ip_private: Optional[str] = None
    vpc_id: Optional[int] = None
    subnet_id: Optional[int] = None


class LoadBalancerResponse(LoadBalancerBase):

    lb_id: int

    model_config = {
        "from_attributes": True
    }
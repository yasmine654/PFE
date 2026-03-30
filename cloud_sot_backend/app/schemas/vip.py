from pydantic import BaseModel
from typing import Optional


class VIPBase(BaseModel):

    subnet_id: int
    loadbalancer_id: int
    mode: str
    resources: Optional[str] = None


class VIPCreate(VIPBase):
    pass


class VIPUpdate(BaseModel):

    subnet_id: Optional[int] = None
    loadbalancer_id: Optional[int] = None
    mode: Optional[str] = None
    resources: Optional[str] = None


class VIPResponse(VIPBase):

    vip_id: int

    model_config = {
        "from_attributes": True
    }
from pydantic import BaseModel
from typing import Optional


class SecurityGroupBase(BaseModel):

    vm_id: int
    direction: str
    port: int
    source: str


class SecurityGroupCreate(SecurityGroupBase):
    pass


class SecurityGroupUpdate(BaseModel):

    vm_id: Optional[int] = None
    direction: Optional[str] = None
    port: Optional[int] = None
    source: Optional[str] = None


class SecurityGroupResponse(SecurityGroupBase):

    sg_id: int

    model_config = {
        "from_attributes": True
    }
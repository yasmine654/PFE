from pydantic import BaseModel
from typing import Optional


class ACLBase(BaseModel):

    subnet_id: int
    direction: str
    source_port: Optional[int] = None          # 🔥
    destination_port: Optional[int] = None     # 🔥
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    action: str

class ACLCreate(ACLBase):
    pass


class ACLUpdate(BaseModel):

    subnet_id: Optional[int] = None
    direction: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    action: Optional[str] = None


class ACLResponse(ACLBase):

    acl_id: int

    model_config = {
        "from_attributes": True
    }
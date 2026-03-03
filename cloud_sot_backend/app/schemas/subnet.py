from pydantic import BaseModel
from typing import Optional


class SubnetBase(BaseModel):
    vpc_id: int
    az_id: int
    cidr: str
    available_ips: Optional[int] = None
    used_ips: Optional[int] = None


class SubnetCreate(SubnetBase):
    pass


class SubnetUpdate(BaseModel):
    vpc_id: Optional[int] = None
    az_id: Optional[int] = None
    cidr: Optional[str] = None
    available_ips: Optional[int] = None
    used_ips: Optional[int] = None


class SubnetResponse(SubnetBase):
    subnet_id: int

    model_config = {
        "from_attributes": True
    }
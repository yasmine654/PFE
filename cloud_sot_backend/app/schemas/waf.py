from pydantic import BaseModel
from typing import Optional


class WAFBase(BaseModel):

    vpc_id: int
    subnet_id: int
    elastic_ip_id: Optional[int] = None


class WAFCreate(WAFBase):
    pass


class WAFUpdate(BaseModel):

    vpc_id: Optional[int] = None
    subnet_id: Optional[int] = None
    elastic_ip_id: Optional[int] = None


class WAFResponse(WAFBase):

    waf_id: int

    model_config = {
        "from_attributes": True
    }
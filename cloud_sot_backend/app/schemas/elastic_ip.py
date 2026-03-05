from pydantic import BaseModel
from typing import Optional


class ElasticIPBase(BaseModel):

    ip: str
    tenant_id: int
    provider_id: int
    region_id: int

    attached: Optional[bool] = None
    attached_to: Optional[str] = None


class ElasticIPCreate(ElasticIPBase):
    pass


class ElasticIPUpdate(BaseModel):

    ip: Optional[str] = None
    tenant_id: Optional[int] = None
    provider_id: Optional[int] = None
    region_id: Optional[int] = None
    attached: Optional[bool] = None
    attached_to: Optional[str] = None


class ElasticIPResponse(ElasticIPBase):

    elastic_ip_id: int

    model_config = {
        "from_attributes": True
    }
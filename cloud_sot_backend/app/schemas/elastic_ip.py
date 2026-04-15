from pydantic import BaseModel
from typing import Optional


class ElasticIPBase(BaseModel):
    ip: str
    provider_id: int
    region_id: int


class ElasticIPCreate(ElasticIPBase):
    pass


class ElasticIPUpdate(BaseModel):
    ip: Optional[str] = None
    provider_id: Optional[int] = None
    region_id: Optional[int] = None


class ElasticIPResponse(ElasticIPBase):
    elastic_ip_id: int
    is_attached: bool = False

    # ✅ AJOUT
    vm_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }
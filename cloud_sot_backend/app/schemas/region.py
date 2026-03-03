from pydantic import BaseModel
from typing import Optional

class RegionBase(BaseModel):
    name: str
    provider_id: int

class RegionCreate(RegionBase):
    pass

class RegionUpdate(BaseModel):
    name: Optional[str] = None
    provider_id: Optional[int] = None

class RegionResponse(RegionBase):
    region_id: int

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }
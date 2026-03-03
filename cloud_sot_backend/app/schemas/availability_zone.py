from pydantic import BaseModel
from typing import Optional


class AvailabilityZoneBase(BaseModel):
    name: str
    region_id: int


class AvailabilityZoneCreate(AvailabilityZoneBase):
    pass


class AvailabilityZoneUpdate(BaseModel):
    name: Optional[str] = None
    region_id: Optional[int] = None


class AvailabilityZoneResponse(AvailabilityZoneBase):
    az_id: int

    model_config = {
        "from_attributes": True
    }
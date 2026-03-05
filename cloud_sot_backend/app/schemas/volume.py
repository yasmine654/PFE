from pydantic import BaseModel
from typing import Optional


class VolumeBase(BaseModel):

    vm_id: Optional[int] = None
    type: Optional[str] = None
    size: int
    encrypted: Optional[bool] = False
    iops: Optional[int] = 0


class VolumeCreate(VolumeBase):
    pass


class VolumeUpdate(BaseModel):

    vm_id: Optional[int] = None
    type: Optional[str] = None
    size: Optional[int] = None
    encrypted: Optional[bool] = None
    iops: Optional[int] = None


class VolumeResponse(VolumeBase):

    volume_id: int

    model_config = {
        "from_attributes": True
    }
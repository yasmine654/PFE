from typing import Optional
from pydantic import BaseModel

class ProviderBase(BaseModel):
    name: str

class ProviderCreate(ProviderBase):
    pass

class ProviderResponse(ProviderBase):
    provider_id: int

    model_config = {
        "from_attributes": True
    }

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
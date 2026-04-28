from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TenantBase(BaseModel):
    name: str
    type: str
    contact: str
    billing_type: str

class TenantCreate(TenantBase):
    pass

class TenantResponse(TenantBase):
    tenant_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    contact: Optional[str] = None
    billing_type: Optional[str] = None
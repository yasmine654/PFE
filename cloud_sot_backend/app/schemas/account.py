from pydantic import BaseModel
from typing import Optional

class AccountBase(BaseModel):
    tenant_id: int
    provider_id: int
    name: str

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    tenant_id: Optional[int] = None
    provider_id: Optional[int] = None
    name: Optional[str] = None

class AccountResponse(AccountBase):
    account_id: int

    model_config = {
        "from_attributes": True
    }
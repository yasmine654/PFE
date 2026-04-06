# app/schemas/conflict.py

from pydantic import BaseModel
from typing import List, Optional

class Conflict(BaseModel):
    type: str
    severity: str
    resource: str
    resource_id: int
    message: str
    related_resources: Optional[List[int]] = []
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from sqlalchemy.sql import func
from app.core.database import Base

class Tenant(Base):
    __tablename__ = "tenant"

    tenant_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20))
    contact = Column(String(150))
    billing_type = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "type IN ('internal','client')",
            name="check_tenant_type"
        ),
        CheckConstraint(
            "billing_type IN ('prepaid','postpaid')",
            name="check_billing_type"
        ),
    )
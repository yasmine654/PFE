from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, UniqueConstraint, Index
)
from app.core.database import Base

class Account(Base):
    __tablename__ = "account"

    account_id = Column(Integer, primary_key=True)

    tenant_id = Column(
        Integer,
        ForeignKey("tenant.tenant_id", ondelete="CASCADE"),
        nullable=False
    )

    provider_id = Column(
        Integer,
        ForeignKey("provider.provider_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "provider_id",
            "name",
            name="unique_account_per_provider"
        ),
        Index("idx_account_tenant", "tenant_id"),
        Index("idx_account_provider", "provider_id"),
    )
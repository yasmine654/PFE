from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, UniqueConstraint, Index
)
from app.core.database import Base

class VPC(Base):
    __tablename__ = "vpc"

    vpc_id = Column(Integer, primary_key=True)

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    region_id = Column(Integer, ForeignKey("region.region_id"))

    cidr = Column(String(50), nullable=False)
    name = Column(String(100))
    state = Column(String(50))

    __table_args__ = (
        UniqueConstraint("cidr", "region_id", name="unique_vpc_cidr_per_region"),
        Index("idx_vpc_tenant", "tenant_id"),
        Index("idx_vpc_region", "region_id"),
    )
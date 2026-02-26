from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, CheckConstraint
)
from app.core.database import Base

class VPCPeering(Base):
    __tablename__ = "vpc_peering"

    peering_id = Column(Integer, primary_key=True)

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))

    vpc_source_id = Column(Integer, ForeignKey("vpc.vpc_id"))
    vpc_target_id = Column(Integer, ForeignKey("vpc.vpc_id"))

    region_source = Column(String(100))
    region_target = Column(String(100))

    __table_args__ = (
        CheckConstraint(
            "vpc_source_id <> vpc_target_id",
            name="check_no_self_peering"
        ),
    )
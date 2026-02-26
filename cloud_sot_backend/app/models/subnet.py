from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, UniqueConstraint, Index
)
from app.core.database import Base

class Subnet(Base):
    __tablename__ = "subnet"

    subnet_id = Column(Integer, primary_key=True)

    vpc_id = Column(
        Integer,
        ForeignKey("vpc.vpc_id", ondelete="CASCADE")
    )

    az_id = Column(
        Integer,
        ForeignKey("availability_zone.az_id")
    )

    cidr = Column(String(50), nullable=False)
    available_ips = Column(Integer)
    used_ips = Column(Integer)

    __table_args__ = (
        UniqueConstraint("cidr", "vpc_id", name="unique_subnet_cidr_per_vpc"),
        Index("idx_subnet_vpc", "vpc_id"),
    )
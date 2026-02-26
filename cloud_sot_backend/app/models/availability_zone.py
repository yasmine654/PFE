from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class AvailabilityZone(Base):
    __tablename__ = "availability_zone"

    az_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    region_id = Column(
        Integer,
        ForeignKey("region.region_id", ondelete="CASCADE")
    )

    __table_args__ = (
        Index("idx_az_region", "region_id"),
    )

    region = relationship("Region", back_populates="availability_zones")
    subnets = relationship("Subnet", back_populates="availability_zone")
    vms = relationship("VM", back_populates="availability_zone")
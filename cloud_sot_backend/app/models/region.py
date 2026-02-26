from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class Region(Base):
    __tablename__ = "region"

    region_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    provider_id = Column(
        Integer,
        ForeignKey("provider.provider_id", ondelete="CASCADE")
    )

    __table_args__ = (
        Index("idx_region_provider", "provider_id"),
    )

    provider = relationship("Provider", back_populates="regions")
    availability_zones = relationship("AvailabilityZone", back_populates="region")
    vpcs = relationship("VPC", back_populates="region")
    vms = relationship("VM", back_populates="region")
    elastic_ips = relationship("ElasticIP", back_populates="region")
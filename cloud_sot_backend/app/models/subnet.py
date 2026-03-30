from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
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
    
    nat_gateways = relationship(
        "NATGateway",
        back_populates="subnet",
        cascade="all, delete-orphan"
    )

    cidr = Column(String(50), nullable=False)
    available_ips = Column(Integer)
    used_ips = Column(Integer)

    __table_args__ = (
        UniqueConstraint("cidr", "vpc_id", name="unique_subnet_cidr_per_vpc"),
        Index("idx_subnet_vpc", "vpc_id"),
    )

    vpc = relationship("VPC", back_populates="subnets")
    availability_zone = relationship("AvailabilityZone", back_populates="subnets")

    vms = relationship(
    "VM",
    back_populates="subnet",
    cascade="all, delete-orphan"
    )

    acls = relationship(
    "ACL",
    back_populates="subnet",
    cascade="all, delete-orphan"
    )

    load_balancers = relationship(
    "LoadBalancer",
    back_populates="subnet",
    cascade="all, delete-orphan"
    )

    vpn_gateways = relationship(
    "VPNGateway",
    back_populates="subnet",
    cascade="all, delete-orphan"
    )

    wafs = relationship(
    "WAF",
    back_populates="subnet",
    cascade="all, delete-orphan"
    )

    nat_gateways = relationship(
        "NATGateway",
        back_populates="subnet",
        cascade="all, delete-orphan"
    )

    vips = relationship(
        "VIP",
        back_populates="subnet",
        cascade="all, delete-orphan"
    )
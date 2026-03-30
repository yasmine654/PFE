from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class VPC(Base):
    __tablename__ = "vpc"

    vpc_id = Column(Integer, primary_key=True)

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"))
    account_id = Column(
    Integer,
    ForeignKey("account.account_id", ondelete="CASCADE"),
    nullable=False
)

    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    region_id = Column(Integer, ForeignKey("region.region_id"))

    cidr = Column(String(50), nullable=False)
    name = Column(String(100))
    state = Column(String(50))

    __table_args__ = (
        UniqueConstraint("cidr", "region_id", name="unique_vpc_cidr_per_region"),
        Index("idx_vpc_tenant", "tenant_id"),
        Index("idx_vpc_region", "region_id"),
        Index("idx_vpc_account", "account_id"),
    )

    tenant = relationship("Tenant", back_populates="vpcs")
    provider = relationship("Provider", back_populates="vpcs")
    region = relationship("Region", back_populates="vpcs")
    account = relationship("Account", back_populates="vpcs")

    subnets = relationship(
        "Subnet",
        back_populates="vpc",
        cascade="all, delete-orphan"
    )

    vms = relationship(
        "VM",
        back_populates="vpc",
        cascade="all, delete-orphan"
    )

    nat_gateways = relationship(
        "NATGateway",
        back_populates="vpc",
        cascade="all, delete-orphan"
    )

    load_balancers = relationship(
        "LoadBalancer",
        back_populates="vpc",
        cascade="all, delete-orphan"
    )

    vpn_gateways = relationship(
        "VPNGateway",
        back_populates="vpc",
        cascade="all, delete-orphan"
    )

    wafs = relationship(
        "WAF",
        back_populates="vpc",
        cascade="all, delete-orphan"
    )

    peerings_source = relationship(
        "VPCPeering",
        foreign_keys="VPCPeering.vpc_source_id",
        cascade="all, delete-orphan"
    )

    peerings_target = relationship(
        "VPCPeering",
        foreign_keys="VPCPeering.vpc_target_id",
        cascade="all, delete-orphan"
    )
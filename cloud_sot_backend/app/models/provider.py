from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Provider(Base):
    __tablename__ = "provider"

    provider_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    accounts = relationship(
        "Account",
        back_populates="provider",
        cascade="all, delete-orphan"
    )

    regions = relationship(
        "Region",
        back_populates="provider",
        cascade="all, delete-orphan"
    )

    vpcs = relationship(
        "VPC",
        back_populates="provider",
        cascade="all, delete-orphan"
    )

    vms = relationship(
        "VM",
        back_populates="provider",
        cascade="all, delete-orphan"
    )

    vpn_gateways = relationship(
        "VPNGateway",
        back_populates="provider",
        cascade="all, delete-orphan"
    )

    elastic_ips = relationship(
        "ElasticIP",
        back_populates="provider",
        cascade="all, delete-orphan"
    )

    vpc_peerings = relationship(
        "VPCPeering",
        back_populates="provider",
        cascade="all, delete-orphan"
    )
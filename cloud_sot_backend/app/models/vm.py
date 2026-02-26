from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.sql import expression
from app.core.database import Base

class VM(Base):
    __tablename__ = "vm"

    vm_id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    region_id = Column(Integer, ForeignKey("region.region_id"))
    az_id = Column(Integer, ForeignKey("availability_zone.az_id"))

    instance_type = Column(String(100))
    vcpu = Column(Integer)
    ram = Column(Integer)

    os = Column(String(100))
    image = Column(String(100))

    private_ip = Column(String(50))
    public_ip = Column(String(50))

    subnet_id = Column(Integer, ForeignKey("subnet.subnet_id"))
    vpc_id = Column(Integer, ForeignKey("vpc.vpc_id"))

    state = Column(String(50))

    __table_args__ = (
        CheckConstraint("vcpu > 0", name="check_vcpu_positive"),
        CheckConstraint("ram > 0", name="check_ram_positive"),

        Index(
            "idx_vm_private_ip_unique",
            "private_ip",
            unique=True,
            postgresql_where=expression.text("private_ip IS NOT NULL")
        ),

        Index("idx_vm_tenant", "tenant_id"),
        Index("idx_vm_subnet", "subnet_id"),
    )
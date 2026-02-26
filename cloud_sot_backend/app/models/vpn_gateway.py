from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from app.core.database import Base

class VPNGateway(Base):
    __tablename__ = "vpn_gateway"

    vpn_id = Column(Integer, primary_key=True)

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))

    type = Column(String(10))

    vpc_id = Column(Integer, ForeignKey("vpc.vpc_id"))
    subnet_id = Column(Integer, ForeignKey("subnet.subnet_id"))

    public_ip = Column(String(50))

    __table_args__ = (
        CheckConstraint(
            "type IN ('ipsec','ssl')",
            name="check_vpn_type"
        ),
    )
from sqlalchemy import Column, Integer, Text, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship


class NATGateway(Base):
    __tablename__ = "nat_gateway"

    nat_id = Column(Integer, primary_key=True)

    vpc_id = Column(
        Integer,
        ForeignKey("vpc.vpc_id")
    )

    subnet_id = Column(
        Integer,
        ForeignKey("subnet.subnet_id")
    )

    snat_rule = Column(Text)
    dnat_rule = Column(Text)

    vpc = relationship("VPC", back_populates="nat_gateways")

    subnet = relationship("Subnet", back_populates="nat_gateways")
from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship


class WAF(Base):
    __tablename__ = "waf"

    waf_id = Column(Integer, primary_key=True)

    vpc_id = Column(Integer, ForeignKey("vpc.vpc_id"))
    subnet_id = Column(Integer, ForeignKey("subnet.subnet_id"))

    elastic_ip_id = Column(
        Integer,
        ForeignKey("elastic_ip.elastic_ip_id")
    )

    vpc = relationship("VPC", back_populates="wafs")
    subnet = relationship("Subnet", back_populates="wafs")

    elastic_ip = relationship(
        "ElasticIP",
        back_populates="waf"
    )
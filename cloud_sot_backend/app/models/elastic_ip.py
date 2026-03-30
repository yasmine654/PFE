from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship

class ElasticIP(Base):
    __tablename__ = "elastic_ip"

    elastic_ip_id = Column(Integer, primary_key=True)

    ip = Column(String(50), nullable=False, unique=True)

    
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    region_id = Column(Integer, ForeignKey("region.region_id"))

    attached = Column(Boolean, server_default="false")
    attached_to = Column(String(100))

    
    provider = relationship("Provider", back_populates="elastic_ips")
    region = relationship("Region", back_populates="elastic_ips")

    vms = relationship("VM", back_populates="elastic_ip")
    vpn_gateways = relationship("VPNGateway", back_populates="elastic_ip")
    wafs = relationship("WAF", back_populates="elastic_ip")
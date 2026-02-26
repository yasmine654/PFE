from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.core.database import Base

class ElasticIP(Base):
    __tablename__ = "elastic_ip"

    elastic_ip_id = Column(Integer, primary_key=True)

    ip = Column(String(50), nullable=False, unique=True)

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    region_id = Column(Integer, ForeignKey("region.region_id"))

    attached = Column(Boolean, server_default="false")
    attached_to = Column(String(100))
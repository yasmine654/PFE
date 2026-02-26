from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class WAF(Base):
    __tablename__ = "waf"

    waf_id = Column(Integer, primary_key=True)

    vpc_id = Column(Integer, ForeignKey("vpc.vpc_id"))
    subnet_id = Column(Integer, ForeignKey("subnet.subnet_id"))

    ip_public = Column(String(50))
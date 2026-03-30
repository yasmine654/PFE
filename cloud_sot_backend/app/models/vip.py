from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class VIP(Base):
    __tablename__ = "vip"

    vip_id = Column(Integer, primary_key=True)

    subnet_id = Column(
        Integer,
        ForeignKey("subnet.subnet_id", ondelete="CASCADE"),
        nullable=False
    )

    loadbalancer_id = Column(
        Integer,
        ForeignKey("load_balancer.lb_id", ondelete="CASCADE"),
        nullable=False
    )

    mode = Column(
        String(20)
    )  # active / passive

    resources = Column(Text)

    subnet = relationship("Subnet", back_populates="vips")

    load_balancer = relationship("LoadBalancer", back_populates="vips")
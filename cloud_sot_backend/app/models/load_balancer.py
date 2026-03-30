from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from app.core.database import Base
from sqlalchemy.orm import relationship

class LoadBalancer(Base):
    __tablename__ = "load_balancer"

    lb_id = Column(Integer, primary_key=True)

    type = Column(String(10))
    ip_private = Column(String(50), nullable=False)

    vpc_id = Column(Integer, ForeignKey("vpc.vpc_id"))
    subnet_id = Column(Integer, ForeignKey("subnet.subnet_id"))

    __table_args__ = (
        CheckConstraint(
            "type IN ('L4','L7')",
            name="check_lb_type"
        ),
    )

    vpc = relationship("VPC", back_populates="load_balancers")
    subnet = relationship("Subnet", back_populates="load_balancers")

    vips = relationship(
        "VIP",
        back_populates="load_balancer",
        cascade="all, delete-orphan"
    )
    
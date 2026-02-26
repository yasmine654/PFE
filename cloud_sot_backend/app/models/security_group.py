from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from app.core.database import Base
from sqlalchemy.orm import relationship

class SecurityGroup(Base):
    __tablename__ = "security_group"

    sg_id = Column(Integer, primary_key=True)

    vm_id = Column(
        Integer,
        ForeignKey("vm.vm_id", ondelete="CASCADE")
    )

    direction = Column(String(10))
    port = Column(Integer)
    source = Column(String(50))

    __table_args__ = (
        CheckConstraint(
            "direction IN ('inbound','outbound')",
            name="check_sg_direction"
        ),
        CheckConstraint(
            "port BETWEEN 1 AND 65535",
            name="check_sg_port"
        ),
    )

    vm = relationship("VM", back_populates="security_groups")
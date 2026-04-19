from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, CheckConstraint
)
from app.core.database import Base
from sqlalchemy.orm import relationship

class ACL(Base):
    __tablename__ = "acl"

    acl_id = Column(Integer, primary_key=True)

    subnet_id = Column(
        Integer,
        ForeignKey("subnet.subnet_id", ondelete="CASCADE")
    )

    direction = Column(String(10))
    source_port = Column(Integer, nullable=True)        # 🔥 NULL = ALL
    destination_port = Column(Integer, nullable=True)   # 🔥 NULL = ALL
    source_ip = Column(String(50))
    destination_ip = Column(String(50))
    action = Column(String(10))

    __table_args__ = (
        CheckConstraint(
            "direction IN ('in','out')",
            name="check_acl_direction"
        ),
        CheckConstraint(
            "action IN ('allow','block')",
            name="check_acl_action"
        ),
        CheckConstraint(
            "(source_port IS NULL OR source_port BETWEEN 1 AND 65535) AND "
            "(destination_port IS NULL OR destination_port BETWEEN 1 AND 65535)",
            name="check_acl_ports"
        ),
    )

    subnet = relationship(
        "Subnet",
        back_populates="acls"
    )
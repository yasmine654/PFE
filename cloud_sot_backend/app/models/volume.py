from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint
from app.core.database import Base
from sqlalchemy.orm import relationship

class Volume(Base):
    __tablename__ = "volume"

    volume_id = Column(Integer, primary_key=True)

    vm_id = Column(
        Integer,
        ForeignKey("vm.vm_id", ondelete="SET NULL")
    )

    type = Column(String(50))
    size = Column(Integer)
    encrypted = Column(Boolean, server_default="false")
    iops = Column(Integer)

    __table_args__ = (
        CheckConstraint("size > 0", name="check_volume_size"),
        CheckConstraint("iops >= 0", name="check_volume_iops"),
    )

    from sqlalchemy.orm import relationship
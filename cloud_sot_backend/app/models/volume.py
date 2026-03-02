import sqlalchemy
from sqlalchemy.orm import relationship
from app.core.database import Base

class Volume(Base):
    __tablename__ = "volume"

    volume_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    vm_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("vm.vm_id", ondelete="SET NULL")
    )

    type = sqlalchemy.Column(sqlalchemy.String(50))
    size = sqlalchemy.Column(sqlalchemy.Integer)
    encrypted = sqlalchemy.Column(sqlalchemy.Boolean, server_default="false")
    iops = sqlalchemy.Column(sqlalchemy.Integer)

    __table_args__ = (
        sqlalchemy.CheckConstraint("size > 0", name="check_volume_size"),
        sqlalchemy.CheckConstraint("iops >= 0", name="check_volume_iops"),
    )

    vm = relationship("VM", back_populates="volumes")
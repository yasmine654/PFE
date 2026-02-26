from sqlalchemy import Column, Integer, String, ForeignKey, Index
from app.core.database import Base

class Region(Base):
    __tablename__ = "region"

    region_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    provider_id = Column(
        Integer,
        ForeignKey("provider.provider_id", ondelete="CASCADE")
    )

    __table_args__ = (
        Index("idx_region_provider", "provider_id"),
    )
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Provider(Base):
    __tablename__ = "provider"

    provider_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
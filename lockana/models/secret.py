from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class Secret(Base):
    __tablename__ = "secrets"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), ForeignKey("users.username"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    encrypted_data = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="secrets")

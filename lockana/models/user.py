from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True, nullable=False)
    totp_secret = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    secrets = relationship("Secret", back_populates="user")
    role = Column(String(256), default="user")
    telegram_connection = Column(Integer, nullable=False, default=0)
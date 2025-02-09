from sqlalchemy import Column, String, Integer, DateTime, func
from .base import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    action = Column(String(255), nullable=False)  # "LOGIN_SUCCESS" | "LOGIN_FAIL"
    timestamp = Column(DateTime, default=func.now())
    ip_address = Column(String(255), nullable=True)

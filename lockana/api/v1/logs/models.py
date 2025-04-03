from pydantic import BaseModel
from datetime import datetime

class LogEntry(BaseModel):
    id: int
    username: str
    action: str
    timestamp: datetime
    ip_address: str

    class Config:
        from_attributes = True 
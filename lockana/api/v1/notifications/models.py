from pydantic import BaseModel

class TelegramConnection(BaseModel):
    telegram_id: str
    username: str 
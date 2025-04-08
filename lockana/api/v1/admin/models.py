from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str 
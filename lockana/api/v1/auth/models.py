from pydantic import BaseModel

class UserAuth(BaseModel):
    username: str
    totp_code: str

class TokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str 
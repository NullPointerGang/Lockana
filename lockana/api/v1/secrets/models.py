from pydantic import BaseModel

class SecretData(BaseModel):
    name: str
    encrypted_data: str

class SecretName(BaseModel):
    name: str 
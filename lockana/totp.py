import pyotp
import base64
import secrets
import datetime
from lockana.exceptions import TOTPCodeException, TOTPSecretException


class TOTPManger:
    def __init__(self):
        self.totp_code_len: int = 6
        self.totp_secre_len: int = 6
        self.totp_minimal_secret_len: int = 6

    def create_totp(self, secret: str) -> pyotp.TOTP:
        if len(secret) < self.totp_minimal_secret_len:
            raise TOTPSecretException('Invalid TOTP secret (secret len < required)!') 
        else:
            return pyotp.TOTP(secret, digits=self.totp_code_len)

    def check_totp_code(self, totp_code: str, secret: str) -> bool:
        if len(secret) < self.totp_minimal_secret_len:
            raise TOTPSecretException('Invalid TOTP secret (secret len < required)!') 
        if len(totp_code) != self.totp_code_len:
            raise TOTPCodeException('Invalid TOTP code (code len != required)!')

        totp = self.create_totp(secret)
        if totp.verify(totp_code):
            return True
        else:
            return False
        
    def create_totp_secret(self):
        secret_bytes = secrets.token_bytes(self.totp_secre_len)
        # Base32 encode the secret and ensure it follows TOTP's expected format
        secret = base64.b32encode(secret_bytes).decode('utf-8').rstrip('=')
        return secret

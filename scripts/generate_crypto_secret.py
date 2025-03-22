from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os
import base64

def generate_key(length: int = 32, use_scrypt: bool = False) -> bytes:
    """
    Генерирует ключ заданной длины.
    :param length: Длина ключа в байтах.
    :param use_scrypt: Использовать ли Scrypt вместо PBKDF2.
    :return: ключ в виде байтовой строки.
    """
    password = os.urandom(16)
    salt = os.urandom(16)
    
    if use_scrypt:
        kdf = Scrypt(
            salt=salt,
            length=length,
            n=2**14,
            r=8,
            p=1
        )
    else:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=100000,
        )
    
    key = kdf.derive(password)
    return key

if __name__ == "__main__":
    key_128 = generate_key(16)
    print(f"Key: {base64.b64encode(key_128).decode()}")

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.backends import default_backend
import os


def chacha20_encrypt_data(data: str, key: bytes) -> str:
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode())
    return f"{nonce.hex()}:{encrypted_data.hex()}"


def chacha20_decrypt_data(encrypted_data: str, key: bytes) -> str:
    nonce_hex, encrypted_data_hex = encrypted_data.split(":")
    nonce = bytes.fromhex(nonce_hex)
    encrypted_data = bytes.fromhex(encrypted_data_hex)
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data)
    return decrypted_data.decode()




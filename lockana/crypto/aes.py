from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def aes_encrypt_data(data: str, key: bytes) -> str:
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return f"{iv.hex()}:{encrypted_data.hex()}"

def aes_decrypt_data(encrypted_data: str, key: bytes) -> str:
    iv_hex, encrypted_data_hex = encrypted_data.split(":")
    iv = bytes.fromhex(iv_hex)
    encrypted_data = bytes.fromhex(encrypted_data_hex)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(decrypted_data) + unpadder.finalize()

    return data.decode()
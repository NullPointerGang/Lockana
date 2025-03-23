from .aes import aes_decrypt_data, aes_encrypt_data
from .rsa import rsa_decrypt_data, rsa_encrypt_data
from .chacha20 import chacha20_decrypt_data, chacha20_encrypt_data

from lockana.config import ENCRYPTION_ALGORITHM

def encrypt_data(data: str, key: bytes) -> str:
    """
    Шифрует данные с использованием выбранного алгоритма шифрования.

    Эта функция принимает открытые данные и шифрует их с использованием алгоритма шифрования, 
    который указан в переменной `ENCRYPTION_ALGORITHM`. Поддерживаемые алгоритмы: AES, RSA, ChaCha20.

    Параметры:
        data (str): Открытые данные, которые нужно зашифровать.
        key (bytes): Ключ для шифрования данных.

    Возвращает:
        str: Зашифрованные данные в строковом формате.

    Исключения:
        ValueError: Если указанный алгоритм шифрования не поддерживается.
    """
    if ENCRYPTION_ALGORITHM.lower() == "aes":
        return aes_encrypt_data(data, key)
    elif ENCRYPTION_ALGORITHM.lower() == "rsa":
        return rsa_encrypt_data(data, key)
    elif ENCRYPTION_ALGORITHM.lower() == "cha20cha20":
        return chacha20_encrypt_data(data, key)
    else:
        raise ValueError("Unsupported encryption algorithm")
    
def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """
    Дешифрует данные с использованием выбранного алгоритма шифрования.

    Эта функция принимает зашифрованные данные и расшифровывает их с использованием алгоритма шифрования, 
    который указан в переменной `ENCRYPTION_ALGORITHM`. Поддерживаемые алгоритмы: AES, RSA, ChaCha20.

    Параметры:
        encrypted_data (str): Зашифрованные данные.
        key (bytes): Ключ для расшифровки данных.

    Возвращает:
        str: Расшифрованные данные в строковом формате.

    Исключения:
        ValueError: Если указанный алгоритм шифрования не поддерживается.
    """
    if ENCRYPTION_ALGORITHM.lower() == "aes":
        return aes_decrypt_data(encrypted_data, key)
    elif ENCRYPTION_ALGORITHM.lower() == "rsa":
        return rsa_decrypt_data(encrypted_data, key)
    elif ENCRYPTION_ALGORITHM.lower() == "cha20cha20":
        return chacha20_decrypt_data(encrypted_data, key)
    else:
        raise ValueError("Unsupported encryption algorithm")
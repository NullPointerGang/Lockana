from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.backends import default_backend
import os


def chacha20_encrypt_data(data: str, key: bytes) -> str:
    """
    Шифрует переданные данные с использованием алгоритма ChaCha20.

    Эта функция генерирует случайный nonce (число, используемое для обеспечения уникальности шифрования),
    шифрует данные с использованием алгоритма ChaCha20 и возвращает nonce вместе с зашифрованными данными 
    в шестнадцатеричном формате.

    Параметры:
        data (str): Открытые данные, которые нужно зашифровать.
        key (bytes): Ключ шифрования.

    Возвращает:
        str: Строка, содержащая nonce и зашифрованные данные в шестнадцатеричном формате, разделенные двоеточием.

    Исключения:
        Exception: Если возникла ошибка при шифровании данных.
    """
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode())
    return f"{nonce.hex()}:{encrypted_data.hex()}"


def chacha20_decrypt_data(encrypted_data: str, key: bytes) -> str:
    """
    Дешифрует переданные зашифрованные данные с использованием алгоритма ChaCha20.

    Эта функция извлекает nonce и зашифрованные данные, затем расшифровывает их с использованием алгоритма ChaCha20,
    и возвращает расшифрованные данные в виде строки.

    Параметры:
        encrypted_data (str): Зашифрованные данные в формате 'nonce:encrypted_data' (где nonce и зашифрованные данные
                               представлены в шестнадцатеричном формате).
        key (bytes): Ключ шифрования.

    Возвращает:
        str: Расшифрованные данные в виде строки.

    Исключения:
        Exception: Если возникла ошибка при расшифровке данных.
    """
    nonce_hex, encrypted_data_hex = encrypted_data.split(":")
    nonce = bytes.fromhex(nonce_hex)
    encrypted_data = bytes.fromhex(encrypted_data_hex)
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data)
    return decrypted_data.decode()




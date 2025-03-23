from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def aes_encrypt_data(data: str, key: bytes) -> str:
    """
    Шифрует переданные данные с использованием AES шифрования в режиме CBC и с добавлением PKCS7 padding.

    Эта функция генерирует случайный вектор инициализации (IV), шифрует данные с использованием AES в режиме CBC,
    и возвращает IV вместе с зашифрованными данными в шестнадцатеричном формате.

    Параметры:
        data (str): Открытые данные, которые нужно зашифровать.
        key (bytes): Ключ шифрования.

    Возвращает:
        str: Строка, содержащая IV и зашифрованные данные в шестнадцатеричном формате, разделенные двоеточием.

    Исключения:
        ValueError: Если входные данные не могут быть правильно дополнены перед шифрованием.
    """
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return f"{iv.hex()}:{encrypted_data.hex()}"

def aes_decrypt_data(encrypted_data: str, key: bytes) -> str:
    """
    Дешифрует переданные зашифрованные данные с использованием AES шифрования в режиме CBC.

    Эта функция извлекает IV и зашифрованные данные, затем расшифровывает их с использованием AES в режиме CBC,
    и возвращает расшифрованные данные в виде строки.

    Параметры:
        encrypted_data (str): Зашифрованные данные в формате 'IV:encrypted_data' (где IV и зашифрованные данные
                               представлены в шестнадцатеричном формате).
        key (bytes): Ключ шифрования.

    Возвращает:
        str: Расшифрованные данные в виде строки.

    Исключения:
        ValueError: Если данные не могут быть правильно расшифрованы.
        Exception: Если произошла ошибка при расшифровке данных.
    """
    iv_hex, encrypted_data_hex = encrypted_data.split(":")
    iv = bytes.fromhex(iv_hex)
    encrypted_data = bytes.fromhex(encrypted_data_hex)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(decrypted_data) + unpadder.finalize()

    return data.decode()
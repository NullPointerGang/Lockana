from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


def rsa_encrypt_data(data: str, public_key) -> str:
    """
    Шифрует данные с использованием RSA и публичного ключа.

    Эта функция принимает открытые данные, шифрует их с использованием алгоритма RSA и возвращает 
    зашифрованные данные в шестнадцатеричном формате.

    Параметры:
        data (str): Открытые данные, которые нужно зашифровать.
        public_key (RSA ключ): Публичный ключ для шифрования данных.

    Возвращает:
        str: Зашифрованные данные в шестнадцатеричном формате.

    Исключения:
        Exception: Если возникла ошибка при шифровании данных.
    """
    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data.hex()

def rsa_decrypt_data(encrypted_data: str, private_key) -> str:
    """
    Дешифрует данные с использованием RSA и приватного ключа.

    Эта функция принимает зашифрованные данные, расшифровывает их с использованием алгоритма RSA
    и возвращает расшифрованные данные в виде строки.

    Параметры:
        encrypted_data (str): Зашифрованные данные в шестнадцатеричном формате.
        private_key (RSA ключ): Приватный ключ для расшифровки данных.

    Возвращает:
        str: Расшифрованные данные в виде строки.

    Исключения:
        Exception: Если возникла ошибка при расшифровке данных.
    """
    encrypted_data_bytes = bytes.fromhex(encrypted_data)
    decrypted_data = private_key.decrypt(
        encrypted_data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data.decode()
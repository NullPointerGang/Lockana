import pyotp
import base64
import secrets
from lockana.config import TOTP_CODE_LEN, TOTP_SECRET_LEN, TOTP_MINIMAL_SECRET_LEN
from lockana.exceptions import TOTPCodeException, TOTPSecretException


class TOTPManger:
    """
    Менеджер для работы с TOTP (Time-Based One-Time Password) — временные одноразовые пароли.

    Этот класс предоставляет функции для создания TOTP-секретов, проверки кодов TOTP и генерации новых секретов.

    Атрибуты:
        totp_code_len (int): Длина генерируемых TOTP кодов. По умолчанию 6 символов.
        totp_secre_len (int): Длина создаваемого TOTP секрета в байтах. По умолчанию 6 байтов.
        totp_minimal_secret_len (int): Минимальная длина секрета TOTP. Секреты короче этого значения считаются недействительными.

    Методы:
        create_totp(secret: str) -> pyotp.TOTP:
            Создаёт объект TOTP для указанного секрета, если его длина соответствует минимальным требованиям.

        check_totp_code(totp_code: str, secret: str) -> bool:
            Проверяет, является ли введённый TOTP код действительным для данного секрета.

        create_totp_secret() -> str:
            Генерирует случайный TOTP секрет, который может быть использован для создания одноразовых паролей.
    """
    def __init__(self):
        """
        Инициализирует менеджер TOTP с дефолтными значениями для длины кода и секрета.
        """
        self.totp_code_len: int = int(TOTP_CODE_LEN)
        self.totp_secret_len: int = int(TOTP_SECRET_LEN)
        self.totp_minimal_secret_len: int = int(TOTP_MINIMAL_SECRET_LEN)

    def create_totp(self, secret: str) -> pyotp.TOTP:
        """
        Создаёт объект TOTP для заданного секрета.

        Аргументы:
            secret (str): Секрет, используемый для создания TOTP.

        Возвращает:
            pyotp.TOTP: Объект TOTP, который может быть использован для генерации одноразовых паролей.

        Исключения:
            TOTPSecretException: Если длина секрета меньше минимально допустимой.
        """
        if len(secret) < self.totp_minimal_secret_len:
            raise TOTPSecretException('Invalid TOTP secret (secret len < required)!') 
        else:
            return pyotp.TOTP(secret, digits=self.totp_code_len)

    def check_totp_code(self, totp_code: str, secret: str) -> bool:
        """
        Проверяет, является ли переданный код TOTP действительным для указанного секрета.

        Аргументы:
            totp_code (str): Код TOTP для проверки.
            secret (str): Секрет, используемый для генерации TOTP.

        Возвращает:
            bool: True, если код верен, иначе False.

        Исключения:
            TOTPSecretException: Если длина секрета меньше минимально допустимой.
            TOTPCodeException: Если длина кода TOTP не соответствует ожидаемой.
        """
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
        """
        Генерирует случайный TOTP секрет для дальнейшего использования.

        Возвращает:
            str: Закодированный в Base32 секрет, готовый для использования в TOTP.
        """
        secret_bytes = secrets.token_bytes(self.totp_secret_len)
        secret = base64.b32encode(secret_bytes).decode('utf-8').rstrip('=')
        return secret

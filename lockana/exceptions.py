from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class LockanaException(Exception):
    """Базовый класс для всех исключений в приложении"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

class AuthenticationError(LockanaException):
    """Ошибки аутентификации"""
    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(message, "AUTH_ERROR")

class AuthorizationError(LockanaException):
    """Ошибки авторизации"""
    def __init__(self, message: str = "Ошибка авторизации"):
        super().__init__(message, "AUTHZ_ERROR")

class ValidationError(LockanaException):
    """Ошибки валидации данных"""
    def __init__(self, message: str = "Ошибка валидации"):
        super().__init__(message, "VALIDATION_ERROR")

class DatabaseError(LockanaException):
    """Ошибки базы данных"""
    def __init__(self, message: str = "Ошибка базы данных"):
        super().__init__(message, "DB_ERROR")

class TOTPError(LockanaException):
    """Базовый класс для ошибок TOTP"""
    def __init__(self, message: str = "Ошибка TOTP", code: str = "TOTP_ERROR"):
        super().__init__(message, code)

class TOTPCodeError(TOTPError):
    """Ошибка кода TOTP"""
    def __init__(self, message: str = "Ошибка кода TOTP"):
        super().__init__(message, "TOTP_CODE_ERROR")

class TOTPSecretError(TOTPError):
    """Ошибка секрета TOTP"""
    def __init__(self, message: str = "Ошибка секрета TOTP"):
        super().__init__(message, "TOTP_SECRET_ERROR")

class CryptoError(LockanaException):
    """Ошибки криптографических операций"""
    def __init__(self, message: str = "Ошибка криптографии"):
        super().__init__(message, "CRYPTO_ERROR")

class HTTPError(HTTPException):
    """Базовый класс для HTTP исключений"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
        code: str = "HTTP_ERROR"
    ):
        self.code = code
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class NotFoundError(HTTPError):
    """Ресурс не найден"""
    def __init__(self, detail: str = "Ресурс не найден"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code="NOT_FOUND"
        )

class BadRequestError(HTTPError):
    """Некорректный запрос"""
    def __init__(self, detail: str = "Некорректный запрос"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            code="BAD_REQUEST"
        )

class UnauthorizedError(HTTPError):
    """Неавторизованный доступ"""
    def __init__(self, detail: str = "Неавторизованный доступ"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="UNAUTHORIZED"
        )

class ForbiddenError(HTTPError):
    """Доступ запрещен"""
    def __init__(self, detail: str = "Доступ запрещен"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code="FORBIDDEN"
        )

class ConflictError(HTTPError):
    """Конфликт данных"""
    def __init__(self, detail: str = "Конфликт данных"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code="CONFLICT"
        )

class RateLimitError(HTTPError):
    """Превышен лимит запросов"""
    def __init__(self, detail: str = "Превышен лимит запросов"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            code="RATE_LIMIT"
        )

class InternalServerError(HTTPError):
    """Внутренняя ошибка сервера"""
    def __init__(self, detail: str = "Внутренняя ошибка сервера"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            code="INTERNAL_SERVER_ERROR"
        )

class RateLimitExceededError(HTTPError):
    """Превышен лимит запросов для конкретного ресурса"""
    def __init__(self, detail: str = "Превышен лимит запросов для данного ресурса"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            code="RATE_LIMIT_EXCEEDED"
        )

class ResourceNotFoundError(HTTPError):
    """Ресурс не найден"""
    def __init__(self, detail: str = "Запрошенный ресурс не найден"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code="RESOURCE_NOT_FOUND"
        )

class InvalidTokenError(HTTPError):
    """Невалидный токен"""
    def __init__(self, detail: str = "Невалидный токен"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="INVALID_TOKEN"
        )

class PermissionDeniedError(HTTPError):
    """Отказ в доступе"""
    def __init__(self, detail: str = "Отказано в доступе"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code="PERMISSION_DENIED"
        )
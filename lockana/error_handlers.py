from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import (
    LockanaException,
    HTTPError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    DatabaseError,
    TOTPError,
    TOTPCodeError,
    TOTPSecretError,
    CryptoError,
    NotFoundError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    RateLimitError,
    InternalServerError,
    RateLimitExceededError,
    ResourceNotFoundError,
    InvalidTokenError,
    PermissionDeniedError
)
from .config import EXCEPTION_CONFIG
import logging

logger = logging.getLogger(__name__)

async def handle_lockana_exception(request: Request, exc: LockanaException):
    """Обработчик для пользовательских исключений"""
    error_config = EXCEPTION_CONFIG["error_codes"].get(
        exc.code,
        EXCEPTION_CONFIG["error_codes"][EXCEPTION_CONFIG["default_error_code"]]
    )
    
    logger.error(f"Ошибка: {exc.message} (код: {exc.code})")
    
    return JSONResponse(
        status_code=error_config["status_code"],
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "type": exc.__class__.__name__
            }
        }
    )

async def handle_http_exception(request: Request, exc: HTTPError):
    """Обработчик для HTTP исключений"""
    error_code = getattr(exc, 'code', EXCEPTION_CONFIG["default_error_code"])
    error_config = EXCEPTION_CONFIG["error_codes"].get(
        error_code,
        EXCEPTION_CONFIG["error_codes"][EXCEPTION_CONFIG["default_error_code"]]
    )
    
    logger.error(f"HTTP ошибка: {exc.detail} (код: {error_code})")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": exc.detail,
                "type": exc.__class__.__name__
            }
        }
    )

async def handle_validation_error(request: Request, exc: ValidationError):
    """Обработчик для ошибок валидации"""
    error_config = EXCEPTION_CONFIG["error_codes"]["VALIDATION_ERROR"]
    
    logger.error(f"Ошибка валидации: {exc.message}")
    
    return JSONResponse(
        status_code=error_config["status_code"],
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": exc.message,
                "type": "ValidationError"
            }
        }
    )

async def handle_database_error(request: Request, exc: DatabaseError):
    """Обработчик для ошибок базы данных"""
    error_config = EXCEPTION_CONFIG["error_codes"]["DB_ERROR"]
    
    logger.error(f"Ошибка базы данных: {exc.message}")
    
    return JSONResponse(
        status_code=error_config["status_code"],
        content={
            "error": {
                "code": "DB_ERROR",
                "message": "Произошла ошибка при работе с базой данных",
                "type": "DatabaseError"
            }
        }
    )

async def handle_totp_error(request: Request, exc: TOTPError):
    """Обработчик для ошибок TOTP"""
    error_config = EXCEPTION_CONFIG["error_codes"].get(
        exc.code,
        EXCEPTION_CONFIG["error_codes"]["TOTP_ERROR"]
    )
    
    logger.error(f"Ошибка TOTP: {exc.message}")
    
    return JSONResponse(
        status_code=error_config["status_code"],
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "type": exc.__class__.__name__
            }
        }
    )

async def handle_crypto_error(request: Request, exc: CryptoError):
    """Обработчик для ошибок криптографии"""
    error_config = EXCEPTION_CONFIG["error_codes"]["CRYPTO_ERROR"]
    
    logger.error(f"Ошибка криптографии: {exc.message}")
    
    return JSONResponse(
        status_code=error_config["status_code"],
        content={
            "error": {
                "code": "CRYPTO_ERROR",
                "message": "Произошла ошибка при криптографических операциях",
                "type": "CryptoError"
            }
        }
    )

async def handle_permission_denied_error(request: Request, exc: PermissionDeniedError):
    """Обработчик для ошибок доступа"""
    logger.error(f"Отказано в доступе: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.detail,
                "type": exc.__class__.__name__
            }
        }
    )

"""Регистрация обработчиков исключений""" 
exception_handlers = {
    LockanaException: handle_lockana_exception,
    HTTPError: handle_http_exception,
    ValidationError: handle_validation_error,
    DatabaseError: handle_database_error,
    TOTPError: handle_totp_error,
    TOTPCodeError: handle_totp_error,
    TOTPSecretError: handle_totp_error,
    CryptoError: handle_crypto_error,
    NotFoundError: handle_http_exception,
    BadRequestError: handle_http_exception,
    UnauthorizedError: handle_http_exception,
    ForbiddenError: handle_http_exception,
    ConflictError: handle_http_exception,
    RateLimitError: handle_http_exception,
    InternalServerError: handle_http_exception,
    AuthenticationError: handle_http_exception,
    AuthorizationError: handle_http_exception,
    RateLimitExceededError: handle_http_exception,
    ResourceNotFoundError: handle_http_exception,
    InvalidTokenError: handle_http_exception,
    PermissionDeniedError: handle_permission_denied_error
} 
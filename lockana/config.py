import os
import yaml
import logging
from typing import Dict, Any

config_path = "config.yaml"

# Проверяем наличие файла конфигурации
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Файл конфигурации '{config_path}' не найден!")

# Загружаем конфигурацию из YAML
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f) or {}

# Проверяем наличие обязательных секций в конфиге
required_sections = ["encryption", "auth", "totp", "jwt", "exceptions", "app"]
for section in required_sections:
    if section not in config:
        logging.error(f"Отсутствует секция '{section}' в конфигурации!")

# Переменные из конфигурации
DATABASE_STRING = os.getenv("DATABASE_STRING", "")
if not DATABASE_STRING:
    raise ValueError("DATABASE_STRING не может быть пустым!")

SECRET_KEY = os.getenv("SECRET_KEY", "").encode()
if not SECRET_KEY:
    raise ValueError("SECRET_KEY не может быть пустым!")

# Настройки JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = config["jwt"].get("access_token_expire_minutes", 1)

# Алгоритм шифрования
ENCRYPTION_ALGORITHM: str = config["encryption"].get("algorithm", "AES")

# Логирование
LOG_FILE_NAME: str = config["logging"].get("filename", "lockana.log")

# Конфигурация аутентификации
BLOCK_TIME_SECONDS: int = config["auth"].get("block_duration_minutes", 5*60) * 60
MAX_LOGIN_ATTEMPTS: int = config["auth"].get("max_login_attempts", 5)
WHITELIST_IPS: list = config["auth"].get("whitelist_ips", [])

# Конфигурация TOTP
TOTP_CODE_LEN: int = config["totp"].get("totp_code_len", 6)
TOTP_SECRET_LEN: int = config["totp"].get("totp_secret_len", 32)
TOTP_MINIMAL_SECRET_LEN: int = config["totp"].get("totp_minimal_secret_len", 16)

# Конфигурация приложения 
APP_PORT: int = config["app"].get("port", 8000)
APP_HOST: str = config["app"].get("host", "0.0.0.0")
APP_PREFIX: str = config["app"].get("prefix", "")

# Настройки CORS
CORS_ENABLED: bool = config["app"]["cros"].get("enabled", True)
CORS_ORIGINS: list = config["app"]["cros"].get("allow_origins", ["*"])
CORS_METHODS: list = config["app"]["cros"].get("allow_methods", ["*"])
CORS_HEADERS: list = config["app"]["cros"].get("allow_headers", ["*"])
CORS_CREDENTIALS: bool = config["app"]["cros"].get("allow_credentials", True)
CORS_MAX_AGE: int = config["app"]["cros"].get("max_age", 3600)

# Конфигурация исключений
EXCEPTION_CONFIG: Dict[str, Any] = {
    "default_error_code": "INTERNAL_SERVER_ERROR",
    "default_error_message": "Произошла внутренняя ошибка",
    "error_codes": {
        "AUTH_ERROR": {
            "message": "Ошибка аутентификации",
            "status_code": 401
        },
        "AUTHZ_ERROR": {
            "message": "Ошибка авторизации",
            "status_code": 403
        },
        "VALIDATION_ERROR": {
            "message": "Ошибка валидации",
            "status_code": 400
        },
        "DB_ERROR": {
            "message": "Ошибка базы данных",
            "status_code": 500
        },
        "TOTP_ERROR": {
            "message": "Ошибка TOTP",
            "status_code": 400
        },
        "CRYPTO_ERROR": {
            "message": "Ошибка криптографии",
            "status_code": 500
        },
        "NOT_FOUND": {
            "message": "Ресурс не найден",
            "status_code": 404
        },
        "BAD_REQUEST": {
            "message": "Некорректный запрос",
            "status_code": 400
        },
        "UNAUTHORIZED": {
            "message": "Неавторизованный доступ",
            "status_code": 401
        },
        "FORBIDDEN": {
            "message": "Доступ запрещен",
            "status_code": 403
        },
        "CONFLICT": {
            "message": "Конфликт данных",
            "status_code": 409
        },
        "RATE_LIMIT": {
            "message": "Превышен лимит запросов",
            "status_code": 429
        },
        "INTERNAL_SERVER_ERROR": {
            "message": "Внутренняя ошибка сервера",
            "status_code": 500
        }
    }
}
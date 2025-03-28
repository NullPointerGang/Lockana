import os
import yaml
import logging

config_path = "config.yaml"

# Проверяем наличие файла конфигурации
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Файл конфигурации '{config_path}' не найден!")

# Загружаем конфигурацию из YAML
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f) or {}

# Проверяем наличие обязательных секций в конфиге
required_sections = ["database", "encryption", "auth", "totp", "jwt"]
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

# Конфигурация TOTP
TOTP_CODE_LEN: int = config["totp"].get("totp_code_len", 6)
TOTP_SECRET_LEN: int = config["totp"].get("totp_secret_len", 32)
TOTP_MINIMAL_SECRET_LEN: int = config["totp"].get("totp_minimal_secret_len", 16)
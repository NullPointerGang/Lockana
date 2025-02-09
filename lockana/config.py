import os
import yaml

config_path = "config.yaml"

if not os.path.exists(config_path):
    raise FileNotFoundError(f"Файл конфигурации '{config_path}' не найден!")

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f) or {}

if "database" not in config:
    raise KeyError("Отсутствует секция 'database' в config.yaml!")

if "host" not in config["database"]:
    raise KeyError("Отсутствует ключ 'host' в секции 'database'!")


DATABASE_HOST = config["database"]["host"]
DATABASE_PORT = config["database"].get("port", 3306) 
DATABASE_NAME = config["database"].get("name", "lockana")
DATABASE_USER = os.getenv("MYSQL_USER", "root")
DATABASE_PASSWORD = os.getenv("MYSQL_PASSWORD")

SECRET_KEY = os.getenv("SECRET_KEY", "").encode()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config["jwt"].get("access_token_expire_minutes", 1)

LOG_FILE_NAME = config["logging"].get("filename", "lockana.log")

print(SECRET_KEY)
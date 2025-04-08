from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from lockana.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from lockana import logging_config  
import logging
import redis


BLACKLISTED_TOKENS = "blacklisted_tokens"

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_jwt_token(token: str = Depends(oauth2_scheme), required_role: str = "user"):
    """
    Проверяет и декодирует JWT токен, а также валидирует роль пользователя.

    Эта функция извлекает информацию из переданного JWT токена, проверяет его действительность и 
    роль пользователя. Также выполняется проверка на отозванные токены, используя Redis.

    Параметры:
        token (str): JWT токен, который необходимо проверить.
        required_role (str): Роль, необходимая для доступа (по умолчанию "user").

    Возвращает:
        str: Имя пользователя, если токен действителен и пользователь имеет требуемую роль.

    Исключения:
        HTTPException: Если токен отозван, имеет недействительные данные, или роль пользователя 
        не соответствует требуемой, возвращается ошибка с кодом 401 (Unauthorized).

    Логирование:
        В случае успешной проверки токена и роли пользователя, функция логирует успешную валидацию.
        В случае ошибок — записывает предупреждения и ошибки.
    """
    try:
        if redis_client.sismember(BLACKLISTED_TOKENS, str(token)):
            logger.warning("Попытка использования отозванного токена.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )
        
        if JWT_SECRET_KEY is None:
            logger.error("JWT_SECRET_KEY не установлен.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
            
        payload = jwt.decode(str(token), JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = str(payload.get("sub"))
        user_role: str = str(payload.get("role"))

        if username is None or (user_role != required_role and user_role != "admin"):
            logger.warning(f"Ошибка валидации токена для пользователя: {username}. Роль: {user_role}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials or insufficient permissions",
            )
        
        return username
    except JWTError as e:
        logger.error(f"Ошибка декодирования токена: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке токена: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def create_jwt_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)):
    """
    Создает новый JWT токен с указанными данными и сроком действия.

    Эта функция генерирует новый токен доступа на основе переданных данных, добавляя информацию о времени 
    истечения токена (по умолчанию это время, определенное в настройках). Токен также включает роль пользователя.

    Параметры:
        data (dict): Данные, которые должны быть включены в токен (например, имя пользователя).
        expires_delta (timedelta): Время, через которое токен станет недействительным (по умолчанию 15 минут).

    Возвращает:
        str: Закодированный JWT токен.

    Примечания:
        - Время истечения токена добавляется в поле "exp".
        - Если роль не указана в данных, по умолчанию используется роль "user".
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    role = data.get("role", "user")
    to_encode.update({"role": role})
    
    if JWT_SECRET_KEY is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def jwt_is_blocked(username: str, ip: str) -> bool:
    """
    Проверяет, заблокирован ли пользователь или его IP-адрес.

    Эта функция проверяет, находится ли пользователь с указанным именем или его IP-адрес в списке заблокированных.
    Для проверки используются ключи в Redis, которые представляют собой блокировки по имени пользователя и IP-адресу.

    Параметры:
        username (str): Имя пользователя, для которого проверяется блокировка.
        ip (str): IP-адрес, для которого проверяется блокировка.

    Возвращает:
        bool: True, если пользователь или его IP-адрес заблокированы, иначе False.
    """
    if redis_client.exists(f"block_user:{username}") or redis_client.exists(f"block_ip:{ip}"):
        return True
    
    return False
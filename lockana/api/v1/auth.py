from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from lockana.database.database import get_db
from lockana.models import User, Log
from lockana.totp import TOTPManger
from lockana.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, BLOCK_TIME_SECONDS, MAX_LOGIN_ATTEMPTS
from lockana import logging_config  
import logging
import redis


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

totp_manager = TOTPManger()
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

BLACKLISTED_TOKENS = "blacklisted_tokens"

class UserAuth(BaseModel):
    username: str
    totp_code: str

def verify_token(token: str = Depends(oauth2_scheme), required_role: str = "user"):
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
    if redis_client.sismember(BLACKLISTED_TOKENS, token):
        logger.warning("Попытка использования отозванного токена.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
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


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)):
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
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def is_blocked(username: str, ip: str) -> bool:
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
    return redis_client.exists(f"block_user:{username}") or redis_client.exists(f"block_ip:{ip}")


@router.post("/login")
def login(request: Request, request_body: UserAuth, db: Session = Depends(get_db)):
    """
    Выполняет аутентификацию пользователя и генерирует JWT токен.

    Эта функция проверяет данные, отправленные пользователем при входе (имя пользователя и код TOTP), и выполняет аутентификацию.
    Если аутентификация успешна, генерируется JWT токен и отправляется в ответе. Если неудачная попытка входа,
    количество неудачных попыток увеличивается и, при превышении максимального количества, IP или имя пользователя блокируются.

    Параметры:
        request (Request): Запрос, содержащий информацию о клиенте (например, IP-адрес).
        request_body (UserAuth): Объект, содержащий данные для аутентификации пользователя (имя пользователя и код TOTP).
        db (Session): Объект сессии для работы с базой данных.

    Возвращает:
        JSONResponse: Ответ с успешным результатом и токеном, либо с ошибкой в случае неудачной аутентификации.
    
    Логирование:
        - Успешный вход: log с IP-адресом и именем пользователя.
        - Неудачные попытки входа: увеличивается счетчик попыток в Redis.
        - Блокировка пользователей и IP-адресов: если количество неудачных попыток превышает максимальное количество.
        - Ошибки: логируются в случае исключений.
    """
    client_ip = request.client.host if request.client else '???'
    username = request_body.username

    if is_blocked(username, client_ip):
        logger.warning(f"Блокированная попытка входа: {username} с IP {client_ip}")
        return JSONResponse(content={"error": "Too many failed attempts. Try again later."}, status_code=429)

    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user_secret: str = str(user.totp_secret)
            valid_code: bool = totp_manager.check_totp_code(request_body.totp_code, user_secret)
            if valid_code:
                redis_client.delete(f"fail_user:{username}")
                redis_client.delete(f"fail_ip:{client_ip}")

                jwt_token = create_access_token({"sub": username, "role": user.role})
                response = {
                    "message": "Login successful",
                    "access_token": jwt_token,
                    "token_type": "bearer"
                }
                db.add(Log(username=username, action='LOGIN_SUCCESS', ip_address=client_ip))
                db.commit()
                logger.info(f"Успешный вход: {username} с IP {client_ip}")
                return JSONResponse(content=response, status_code=200)

        redis_client.incr(f"fail_user:{username}")
        redis_client.incr(f"fail_ip:{client_ip}")

        attempts_user = int(redis_client.get(f"fail_user:{username}") or 0)
        attempts_ip = int(redis_client.get(f"fail_ip:{client_ip}") or 0)

        if attempts_user >= MAX_LOGIN_ATTEMPTS:
            redis_client.setex(f"block_user:{username}", BLOCK_TIME_SECONDS, "1")
        if attempts_ip >= MAX_LOGIN_ATTEMPTS:
            redis_client.setex(f"block_ip:{client_ip}", BLOCK_TIME_SECONDS, "1")

        logger.warning(f"Неудачная попытка входа: {username} с IP {client_ip}")
        db.add(Log(username=username, action='LOGIN_FAIL', ip_address=client_ip))
        db.commit()

        return JSONResponse(content={"error": "Invalid auth data"}, status_code=401)

    except Exception as error:
        logger.error(f"Ошибка входа: {str(error)}")
        return JSONResponse(content={"error": "An error occurred"}, status_code=500)

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    """
    Завершающий процесс для пользователя: удаление токена из активных.

    Эта функция позволяет пользователю выйти из системы, добавляя его токен в черный список.
    После этого токен считается отозванным, и его больше нельзя использовать для доступа к защищенным ресурсам.

    Параметры:
        token (str): Токен доступа пользователя, получаемый через механизм OAuth2.

    Возвращает:
        JSONResponse: Ответ с успешным сообщением о выходе из системы.

    Логирование:
        - Запись в лог с сообщением, что пользователь вышел из системы.
    """
    redis_client.sadd(BLACKLISTED_TOKENS, token)
    logger.info("Пользователь вышел из системы.")
    return JSONResponse(content={"message": "Logged out successfully"}, status_code=200)
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
from lockana.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
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
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    role = data.get("role", "user")
    to_encode.update({"role": role})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


@router.post("/login")
def login(request: Request, request_body: UserAuth, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else '???'

    try:
        user = db.query(User).filter(User.username == request_body.username).first()
        if user:
            user_secret: str = str(user.totp_secret)
            valid_code: bool = totp_manager.check_totp_code(request_body.totp_code, user_secret)
            if valid_code:
                jwt_token = create_access_token({"sub": request_body.username, "role": user.role})
                response = {
                    "message": "Login successful",
                    "access_token": jwt_token,
                    "token_type": "bearer"
                }
                db.add(Log(username=request_body.username, action='LOGIN_SUCCESS', ip_address=client_ip))
                db.commit()
                logger.info(f"Успешный вход: {request_body.username} с IP {client_ip}")
                return JSONResponse(content=response, status_code=200)
            else:
                logger.warning(f"Неудачная попытка входа (неверный код TOTP): {request_body.username} с IP {client_ip}")
        else:
            logger.warning(f"Неудачная попытка входа (пользователь не найден): {request_body.username} с IP {client_ip}")

        response = {"code": 401, "error": "Invalid auth data"}
        db.add(Log(username=request_body.username, action='LOGIN_FAIL', ip_address=client_ip))
        db.commit()
        return JSONResponse(content=response, status_code=401)

    except Exception as error:
        logger.error(f"Ошибка входа: {str(error)}")
        response = {"code": 500, "error": "An error occurred on the server side"}
        db.add(Log(username=request_body.username, action='LOGIN_FAIL', ip_address=client_ip))
        db.commit()
        return JSONResponse(content=response, status_code=500)


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    redis_client.sadd(BLACKLISTED_TOKENS, token)
    logger.info("Пользователь вышел из системы.")
    return JSONResponse(content={"message": "Logged out successfully"}, status_code=200)

@router.get("/protected")
def protected(token: str = Depends(oauth2_scheme)):
    try:
        return JSONResponse(content={"message": "Welcome to the protected route!"}, status_code=200)
    except Exception as error:
        logger.error(f"Ошибка доступа к защищенному маршруту: {str(error)}")
        response = {"code": 500, "error": "An error occurred while accessing the protected route"}
        return JSONResponse(content=response, status_code=500)

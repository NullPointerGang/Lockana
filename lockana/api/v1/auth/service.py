from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from lockana.models import User, Log
from lockana.totp import TOTP_MANAGER
from lockana.config import BLOCK_TIME_SECONDS, MAX_LOGIN_ATTEMPTS, WHITELIST_IPS
from .jwt import jwt_is_blocked, create_jwt_access_token, redis_client, BLACKLISTED_TOKENS
from lockana.exceptions import RateLimitExceededError, AuthenticationError, TOTPCodeError, TOTPSecretError
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, request: Request, username: str, totp_code: str):
        try:
            client_ip = request.client.host if request.client else '???'

            if jwt_is_blocked(username, client_ip) and client_ip not in WHITELIST_IPS:
                logger.warning(f"Блокированная попытка входа: {username} с IP {client_ip}")
                raise RateLimitExceededError("Too many failed attempts. Try again later.")

            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                self._handle_failed_login(username, client_ip)
                raise AuthenticationError("Invalid username or TOTP code")

            user_secret = str(user.totp_secret)
            try:
                if not TOTP_MANAGER.check_totp_code(totp_code, user_secret):
                    self._handle_failed_login(username, client_ip)
                    raise AuthenticationError("Invalid username or TOTP code")
            except (TOTPCodeError, TOTPSecretError) as e:
                self._handle_failed_login(username, client_ip)
                raise AuthenticationError("Invalid username or TOTP code")

            redis_client.delete(f"fail_user:{username}")
            redis_client.delete(f"fail_ip:{client_ip}")

            user_role = "user"
            if user.roles:
                admin_role = next((role for role in user.roles if role.name == "admin"), None)
                if admin_role:
                    user_role = "admin"
                else:
                    user_role = user.roles[0].name

            jwt_token = create_jwt_access_token({"sub": username, "role": user_role})

            self.db.add(Log(username=username, action='LOGIN_SUCCESS', ip_address=client_ip))
            self.db.commit()
            logger.info(f"Успешный вход: {username}")

            return {
                "message": "Login successful",
                "access_token": jwt_token,
                "token_type": "bearer"
            }

        except (RateLimitExceededError, AuthenticationError):
            raise
        except Exception as error:
            logger.error(f"Ошибка входа: {str(error)}")
            raise HTTPException(status_code=500, detail="An error occurred during authentication")

    def logout(self, token: str):
        try:
            redis_client.sadd(BLACKLISTED_TOKENS, token)
            logger.info("Пользователь вышел из системы.")
            return {"message": "Logged out successfully"}
        except Exception as error:
            logger.error(f"Ошибка выхода: {str(error)}")
            raise HTTPException(status_code=500, detail="An error occurred")

    def _handle_failed_login(self, username: str, client_ip: str):
        redis_client.incr(f"fail_user:{username}")
        redis_client.incr(f"fail_ip:{client_ip}")

        attempts_user = int(redis_client.get(f"fail_user:{username}") or 0)
        attempts_ip = int(redis_client.get(f"fail_ip:{client_ip}") or 0)

        if attempts_user >= MAX_LOGIN_ATTEMPTS:
            redis_client.setex(f"block_user:{username}", BLOCK_TIME_SECONDS, "1")
        if attempts_ip >= MAX_LOGIN_ATTEMPTS:
            redis_client.setex(f"block_ip:{client_ip}", BLOCK_TIME_SECONDS, "1")

        logger.warning(f"Неудачная попытка входа: {username} с IP {client_ip}")
        self.db.add(Log(username=username, action='LOGIN_FAIL', ip_address=client_ip))
        self.db.commit() 
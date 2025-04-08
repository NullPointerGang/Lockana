from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from lockana.database.database import get_db
from .models import UserAuth, TokenResponse
from .service import AuthService
from .jwt import oauth2_scheme
from lockana.exceptions import (
    InvalidTokenError,
    RateLimitExceededError,
    InternalServerError
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
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
    """
    try:
        service = AuthService(db)
        result = service.login(request, request_body.username, request_body.totp_code)
        return JSONResponse(content=result, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    except InvalidTokenError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except RateLimitExceededError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise InternalServerError(detail="Internal server error during login")

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Завершающий процесс для пользователя: удаление токена из активных.

    Эта функция позволяет пользователю выйти из системы, добавляя его токен в черный список.
    После этого токен считается отозванным, и его больше нельзя использовать для доступа к защищенным ресурсам.

    Параметры:
        token (str): Токен доступа пользователя, получаемый через механизм OAuth2.
        db (Session): Объект сессии для работы с базой данных.

    Возвращает:
        JSONResponse: Ответ с успешным сообщением о выходе из системы.
    """
    try:
        service = AuthService(db)
        result = service.logout(token)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=getattr(e, 'status_code', 500)) 
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from lockana.database.database import get_db
from lockana.api.v1.auth.jwt import oauth2_scheme, verify_jwt_token
from lockana.permissions import check_permission
from .models import TelegramConnection
from .service import NotificationService
from lockana.exceptions import (
    InvalidTokenError,
    InternalServerError
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/test")
@check_permission("read")
def test_notification(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Тестирует отправку уведомления пользователю.

    Args:
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        JSONResponse: Ответ с сообщением о статусе операции.
    """
    username: str = verify_jwt_token(token)
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = NotificationService(db)
        service.test_notification(username)
        return JSONResponse({"message": "Test notification sent successfully"}, status_code=200)
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error testing notification: {e}")
        raise InternalServerError(detail="Error testing notification")

@router.post("/telegram/connect")
@check_permission("write")
def connect_telegram(connection: TelegramConnection, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Подключает Telegram для получения уведомлений.

    Args:
        connection (TelegramConnection): Данные для подключения Telegram.
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        JSONResponse: Ответ с сообщением о статусе операции.
    """
    username: str = verify_jwt_token(token)
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = NotificationService(db)
        service.connect_telegram(username, connection.telegram_id, connection.telegram_username)
        return JSONResponse({"message": "Telegram connected successfully"}, status_code=200)
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error connecting telegram: {e}")
        raise InternalServerError(detail="Error connecting telegram") 
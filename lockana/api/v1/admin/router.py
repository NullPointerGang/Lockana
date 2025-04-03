from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from lockana.database.database import get_db
from lockana.api.v1.auth.jwt import oauth2_scheme, verify_jwt_token
from lockana.permissions import check_permission
from .models import CreateUser
from .service import AdminService
from lockana.exceptions import (
    InvalidTokenError,
    ResourceNotFoundError,
    PermissionDeniedError,
    InternalServerError
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/users/create")
@check_permission("manage")
def create_user(user_data: CreateUser, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Создает нового пользователя в базе данных.

    Args:
        user_data (CreateUser): Данные нового пользователя.
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        JSONResponse: Ответ с сообщением о статусе операции.
            - 201: Пользователь успешно создан.
            - 401: Ошибка аутентификации.
            - 500: Внутренняя ошибка сервера.
    """
    username: str = verify_jwt_token(token, required_role="admin")
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = AdminService(db)
        user_id = service.create_user(user_data.username)
        return JSONResponse({"message": "User created successfully", "user_id": user_id}, status_code=201)
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise InternalServerError(detail="Error creating user")

@router.delete("/users/delete")
@check_permission("manage")
def delete_user(user_data: CreateUser, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Удаляет пользователя из базы данных.

    Args:
        user_data (CreateUser): Данные пользователя для удаления.
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        JSONResponse: Ответ с сообщением о статусе операции.
            - 200: Пользователь успешно удален.
            - 404: Пользователь не найден.
            - 401: Ошибка аутентификации.
            - 500: Внутренняя ошибка сервера.
    """
    username: str = verify_jwt_token(token, required_role="admin")
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = AdminService(db)
        service.delete_user(user_data.username)
        return JSONResponse({"message": "User deleted successfully"}, status_code=200)
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except ResourceNotFoundError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise InternalServerError(detail="Error deleting user")

@router.get("/users/list")
@check_permission("manage")
def list_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Возвращает список всех пользователей в базе данных.

    Args:
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        JSONResponse: Ответ с массивом пользователей или сообщением об ошибке.
            - 200: Список пользователей успешно получен.
            - 401: Ошибка аутентификации.
            - 500: Внутренняя ошибка сервера.
    """
    username: str = verify_jwt_token(token, required_role="admin")
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = AdminService(db)
        users = service.list_users()
        return JSONResponse({"users": users}, status_code=200)
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise InternalServerError(detail="Error listing users") 
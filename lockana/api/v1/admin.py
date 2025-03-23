from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from lockana.database.database import get_db
from lockana.models import User, Base
from lockana.api.v1.auth import oauth2_scheme, verify_token, totp_manager
from lockana import logging_config  
import logging

class CreateUser(BaseModel):
    username: str
    # telegram_connection: str

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/users/create")
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
    username: str = verify_token(token, required_role="admin")
    try:
        if username:
            # new_user = User(username=user_data.username, telegram_connection=user_data.telegram_connection, totp_secret=totp_manager.create_totp_secret())
            new_user = User(username=user_data.username, totp_secret=totp_manager.create_totp_secret())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return JSONResponse({"message": "User created successfully", "user_id": new_user.id}, status_code=201)
        else:
            return JSONResponse({"code": 401, "error": "Invalid auth data"}, status_code=401)
    except Exception as error:
        logger.error(f"Error creating user: {error}")
        db.rollback()
        return JSONResponse({"message": "Internal server error"}, status_code=500)

@router.delete("/users/delete")
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
    username: str = verify_token(token, required_role="admin")
    try:
        if username:
            user_to_delete = db.query(User).filter(User.username == user_data.username).first()
            if user_to_delete:
                db.delete(user_to_delete)
                db.commit()
                return JSONResponse({"message": "User deleted successfully"}, status_code=200)
            else:
                return JSONResponse({"code": 404, "error": "User not found"}, status_code=404)
        else:
            return JSONResponse({"code": 401, "error": "Invalid auth data"}, status_code=401)
    except Exception as error:
        logger.error(f"Error deleting user: {error}")
        db.rollback()
        return JSONResponse({"message": "Internal server error"}, status_code=500)

@router.get("/users/list")
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
    username: str = verify_token(token, required_role="admin")
    try:
        if username:
            users = db.query(User).all()
            user_list = [{"id": user.id, "username": user.username, "created_at": user.created_at} for user in users]
            return JSONResponse({"users": user_list}, status_code=200)
        else:
            return JSONResponse({"code": 401, "error": "Invalid auth data"}, status_code=401)
    except Exception as error:
        logger.error(f"Error listing users: {error}")
        return JSONResponse({"message": "Internal server error"}, status_code=500)
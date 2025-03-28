from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from lockana.api.v1.auth import oauth2_scheme, verify_token
from lockana.database.database import get_db
from lockana.models import Secret
from lockana.config import SECRET_KEY
from lockana.crypto import encrypt_data, decrypt_data
from lockana.api.v1.permissions import check_permission
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/secrets", tags=["Secrets"])

class SecretData(BaseModel):
    name: str
    encrypted_data: str

class SecretName(BaseModel):
    name: str

@router.get("/list")
@check_permission("read")
def list_secrets(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Возвращает список секретов для аутентифицированного пользователя.

    Args:
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        dict: Словарь с ключом "secrets", содержащий список расшифрованных секретов пользователя.
        
    Raises:
        HTTPException: 
            - 401: Неверный токен.
            - 500: Внутренняя ошибка сервера.
    """
    username = verify_token(token)
    try:
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        secrets = db.query(Secret).filter(Secret.username == username).all()
        logger.info(f"User {username} fetched their secrets.")
        decrypted_secrets = [
            {"name": secret.name, "data": decrypt_data(secret.encrypted_data, SECRET_KEY)}
            for secret in secrets
        ]
        return {"secrets": decrypted_secrets}

    except Exception as e:
        logger.error(f"Error while listing secrets: {str(e)}. Username: {username}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/add")
@check_permission("write")
def add_secret(secret: SecretData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Добавляет новый секрет для аутентифицированного пользователя.

    Args:
        secret (SecretData): Данные секрета, которые включают имя и зашифрованное содержимое.
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        dict: Словарь с сообщением об успешном добавлении секрета и именем секрета.
        
    Raises:
        HTTPException:
            - 401: Неверный токен.
            - 500: Внутренняя ошибка сервера.
    """
    username = verify_token(token)
    try:
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        encrypted_data = encrypt_data(secret.encrypted_data, SECRET_KEY)
        new_secret = Secret(username=username, name=secret.name, encrypted_data=encrypted_data)
        db.add(new_secret)
        db.commit()
        logger.info(f"User {username} added a new secret")
        
        return {"message": "Secret added successfully", "secret": secret.name}

    except Exception as e:
        logger.error(f"Error while adding secret for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/get")
@check_permission("read")
def get_secret(secret_name: SecretName, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Получает секрет по имени для аутентифицированного пользователя.

    Args:
        secret_name (SecretName): Объект с именем секрета, который требуется получить.
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        dict: Словарь с расшифрованными данными секрета.
        
    Raises:
        HTTPException:
            - 401: Неверный токен.
            - 404: Секрет не найден.
            - 500: Внутренняя ошибка сервера.
    """
    username = verify_token(token)
    try:
        name = secret_name.name
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        secret = db.query(Secret).filter(Secret.username == username, Secret.name == name).first()
        
        if not secret:
            logger.warning(f"User {username} tried to access a non-existing secret")
            raise HTTPException(status_code=404, detail="Secret not found")
        
        logger.info(f"User {username} accessed their secret")
        decrypted_data = decrypt_data(secret.encrypted_data, SECRET_KEY)
        return {"secret": decrypted_data}

    except Exception as e:
        logger.error(f"Error while retrieving secret for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/update")
@check_permission("write")
def update_secret(secret: SecretData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Обновляет существующий секрет для аутентифицированного пользователя.

    Args:
        secret (SecretData): Данные секрета, которые включают имя и зашифрованное содержимое для обновления.
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        dict: Словарь с сообщением об успешном обновлении секрета и именем секрета.
        
    Raises:
        HTTPException:
            - 401: Неверный токен.
            - 404: Секрет не найден.
            - 500: Внутренняя ошибка сервера.
    """
    username = verify_token(token)
    try:
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        secret_to_update = db.query(Secret).filter(Secret.username == username, Secret.name == secret.name).first()
        
        if not secret_to_update:
            logger.warning(f"User {username} tried to update a non-existing secret")
            raise HTTPException(status_code=404, detail="Secret not found")
        
        secret_to_update.encrypted_data = encrypt_data(secret.encrypted_data, SECRET_KEY)
        db.commit()
        logger.info(f"User {username} updated their secret")
        
        return {"message": "Secret updated successfully", "secret": secret.name}

    except Exception as e:
        logger.error(f"Error while updating secret for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/delete")
@check_permission("delete")
def delete_secret(secret_name: SecretName, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Удаляет секрет по имени для аутентифицированного пользователя.

    Args:
        secret_name (SecretName): Объект с именем секрета, который требуется удалить.
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        dict: Словарь с сообщением об успешном удалении секрета.

    Raises:
        HTTPException:
            - 401: Неверный токен.
            - 404: Секрет не найден.
            - 500: Внутренняя ошибка сервера.
    """
    username = verify_token(token)
    try:
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        secret = db.query(Secret).filter(Secret.username == username, Secret.name == secret_name.name).first()

        if not secret:
            logger.warning(f"User {username} tried to delete a non-existing secret")
            raise HTTPException(status_code=404, detail="Secret not found")

        db.delete(secret)
        db.commit()
        logger.info(f"User {username} deleted their secret")
        
        return {"message": "Secret deleted successfully"}

    except Exception as e:
        logger.error(f"Error while deleting secret for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

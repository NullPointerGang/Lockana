from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from lockana.database.database import get_db
from lockana.api.v1.auth.jwt import oauth2_scheme, verify_jwt_token
from lockana.permissions import check_permission
from .models import LogEntry
from .service import LogService
from lockana.exceptions import (
    InvalidTokenError,
    ResourceNotFoundError,
    PermissionDeniedError,
    InternalServerError
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/logs-file")
@check_permission("logs-file")
@check_permission("logs-read")
def get_logs_file(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Предоставляет файл логов сервера.

    Args:
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        FileResponse: Файл логов в виде бинарных данных.
        JSONResponse: Ответ с сообщением об ошибке в случае проблем.
    """
    username: str = verify_jwt_token(token, required_role="admin")
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = LogService(db)
        log_file_path = service.get_logs_file()
        return FileResponse(log_file_path, media_type='application/octet-stream', filename="logs.txt")
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except ResourceNotFoundError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error occurred while retrieving log file: {e}")
        raise InternalServerError(detail="Error retrieving log file")

@router.delete("/logs-file")
@check_permission("logs-file")
@check_permission("logs-delete")
def delete_logs_file(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Удаляет файл логов сервера.

    Args:
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        JSONResponse: Ответ с сообщением о статусе операции.
    """
    username: str = verify_jwt_token(token, required_role="admin")
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = LogService(db)
        service.delete_logs_file()
        return JSONResponse({"message": "Log file deleted successfully"}, status_code=200)
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except ResourceNotFoundError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error when deleting a log file: {e}")
        raise InternalServerError(detail="Error deleting log file")

@router.get("/auth-logs")
@check_permission("logs")
@check_permission("logs-read")
def get_logs(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Возвращает список логов действий пользователей.

    Args:
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        JSONResponse: Ответ с массивом логов или сообщением об ошибке.
    """
    username: str = verify_jwt_token(token, required_role="admin")
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = LogService(db)
        logs = service.get_auth_logs()
        return JSONResponse({"logs": [LogEntry.from_orm(log).dict() for log in logs]})
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error occurred while retrieving the log: {e}")
        raise InternalServerError(detail="Error retrieving auth logs")

@router.delete("/auth-logs")
@check_permission("logs")
@check_permission("logs-delete")
def delete_logs(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Удаляет все записи логов из базы данных.

    Args:
        token (str, optional): Токен аутентификации, получаемый через OAuth2.
        db (Session, optional): Сессия базы данных.

    Returns:
        JSONResponse: Ответ с сообщением о статусе операции.
    """
    username: str = verify_jwt_token(token, required_role="admin")
    try:
        if not username:
            raise InvalidTokenError("Invalid auth data")
        
        service = LogService(db)
        deleted_count = service.delete_auth_logs()
        return JSONResponse({"message": f"Successfully deleted {deleted_count} logs from the database"}, status_code=200)
    except InvalidTokenError as e:
        return JSONResponse({"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error occurred while deleting logs: {e}")
        raise InternalServerError(detail="Error deleting auth logs") 
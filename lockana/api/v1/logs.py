from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from lockana.api.v1.auth import oauth2_scheme, verify_token
from lockana.database.database import get_db
from lockana.models import Log
from lockana import logging_config  
from lockana.config import LOG_FILE_NAME
import logging
import os


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/logs-file")
def get_logs_file(token: str = Depends(oauth2_scheme)):
    username: str = verify_token(token, required_role="admin")
    try:
        if username:
            log_file_path = os.path.join(os.getcwd(), LOG_FILE_NAME)
            if not os.path.exists(log_file_path):
                logger.error(f"Log file {LOG_FILE_NAME} does not exist.")
                return JSONResponse(status_code=404, content={"message": "Log file not found"})

            return FileResponse(log_file_path, media_type='application/octet-stream', filename=LOG_FILE_NAME)
        else:
            return JSONResponse({"code": 401, "error": "Invalid auth data"}, status_code=401)
    except Exception as error:
        logger.error(f"Error occurred while retrieving log file: {error}")
        return JSONResponse({"message": "Internal server error"}, status_code=500)


@router.get("/logs")
def get_logs(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username: str = verify_token(token, required_role="admin")
    try:
        if username:
            logs: list[Log] = db.query(Log).all()
            log_list = [
                {"id": log.id, "username": log.username, "action": log.action, 
                 "timestamp": log.timestamp, "ip_address": log.ip_address} 
                for log in logs
            ]
            return JSONResponse({"logs": log_list})
        else:
            return JSONResponse({"code": 401, "error": "Invalid auth data"}, status_code=401)
    except Exception as error:
        logger.error(f"Error occurred while retrieving the log: {error}")
        return JSONResponse({"message": "Internal server error"}, status_code=500)

@router.delete("logs-file")
def delete_logs_file(token: str = Depends(oauth2_scheme)):
    username: str = verify_token(token, required_role="admin")
    try:
        if username:
            log_file_path = os.path.join(os.getcwd(), LOG_FILE_NAME)
            if not os.path.exists(log_file_path):
                logger.error(f"Log file {LOG_FILE_NAME} does not exist.")
                return JSONResponse(status_code=404, content={"message": "Log file not found"})

            os.remove(log_file_path)

            return JSONResponse({"code": 200, "message": "The log file has been successfully deleted"})       
        else:
            return JSONResponse({"code": 401, "error": "Invalid auth data"}, status_code=401)
    except Exception as error:
        logger.error(f"Error when deleting a log file: {error}")
        return JSONResponse({"message": "Internal server error"}, status_code=500)


@router.delete("/logs")
def delete_logs(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username: str = verify_token(token, required_role="admin")
    try:
        if username:
            deleted_count = db.query(Log).delete()
            db.commit()
            logger.info(f"Deleted {deleted_count} logs from the database.")
            return JSONResponse({"code": 200, "message": f"Successfully deleted {deleted_count} logs from the database"})
        else:
            return JSONResponse({"code": 401, "error": "Invalid auth data"}, status_code=401)
    except Exception as error:
        db.rollback()
        logger.error(f"Error occurred while deleting logs: {error}")
        return JSONResponse({"message": "Internal server error"}, status_code=500)

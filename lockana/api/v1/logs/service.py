from sqlalchemy.orm import Session
from fastapi import HTTPException
from lockana.models import Log
from lockana.config import LOG_FILE_NAME
from lockana.exceptions import (
    ResourceNotFoundError,
    InternalServerError
)
import logging
import os

logger = logging.getLogger(__name__)

class LogService:
    def __init__(self, db: Session):
        self.db = db

    def get_logs_file(self):
        try:
            log_file_path = os.path.join(os.getcwd(), LOG_FILE_NAME)
            if not os.path.exists(log_file_path):
                logger.error(f"Log file {LOG_FILE_NAME} does not exist.")
                raise ResourceNotFoundError(detail="Log file not found")
            return log_file_path
        except ResourceNotFoundError:
            raise
        except Exception as error:
            logger.error(f"Error occurred while retrieving log file: {error}")
            raise InternalServerError(detail="Error retrieving log file")

    def delete_logs_file(self):
        try:
            log_file_path = os.path.join(os.getcwd(), LOG_FILE_NAME)
            if not os.path.exists(log_file_path):
                logger.error(f"Log file {LOG_FILE_NAME} does not exist.")
                raise ResourceNotFoundError(detail="Log file not found")
            os.remove(log_file_path)
            return True
        except ResourceNotFoundError:
            raise
        except Exception as error:
            logger.error(f"Error when deleting a log file: {error}")
            raise InternalServerError(detail="Error deleting log file")

    def get_auth_logs(self):
        try:
            logs = self.db.query(Log).all()
            return logs
        except Exception as error:
            logger.error(f"Error occurred while retrieving the log: {error}")
            raise InternalServerError(detail="Error retrieving auth logs")

    def delete_auth_logs(self):
        try:
            deleted_count = self.db.query(Log).delete()
            self.db.commit()
            logger.info(f"Deleted {deleted_count} logs from the database.")
            return deleted_count
        except Exception as error:
            self.db.rollback()
            logger.error(f"Error occurred while deleting logs: {error}")
            raise InternalServerError(detail="Error deleting auth logs") 
from sqlalchemy.orm import Session
from lockana.exceptions import InternalServerError
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def test_notification(self, username: str):
        try:
            # TODO: Implement notification logic
            return True
        except Exception as error:
            logger.error(f"Error testing notification: {error}")
            raise InternalServerError(detail="Error testing notification")

    def connect_telegram(self, username: str, telegram_id: str, telegram_username: str):
        try:
            # TODO: Implement notification logic
            return True
        except Exception as error:
            logger.error(f"Error connecting telegram: {error}")
            raise InternalServerError(detail="Error connecting telegram") 
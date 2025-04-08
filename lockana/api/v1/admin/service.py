from sqlalchemy.orm import Session
from lockana.models import User
from lockana.totp import TOTP_MANAGER
from lockana.exceptions import (
    ResourceNotFoundError,
    InternalServerError
)
import logging

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str):
        try:
            new_user = User(username=username, totp_secret=TOTP_MANAGER.create_totp_secret())
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user.id
        except Exception as error:
            logger.error(f"Error creating user: {error}")
            self.db.rollback()
            raise InternalServerError(detail="Error creating user")

    def delete_user(self, username: str):
        try:
            user_to_delete = self.db.query(User).filter(User.username == username).first()
            if not user_to_delete:
                logger.warning(f"Attempt to delete non-existent user: {username}")
                raise ResourceNotFoundError(detail="User not found")
            
            self.db.delete(user_to_delete)
            self.db.commit()
        except ResourceNotFoundError:
            raise
        except Exception as error:
            logger.error(f"Error deleting user: {error}")
            self.db.rollback()
            raise InternalServerError(detail="Error deleting user")

    def list_users(self):
        try:
            users = self.db.query(User).all()
            return [{"id": user.id, "username": user.username, "created_at": user.created_at} for user in users]
        except Exception as error:
            logger.error(f"Error listing users: {error}")
            raise InternalServerError(detail="Error listing users") 
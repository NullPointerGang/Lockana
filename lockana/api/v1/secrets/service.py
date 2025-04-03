from sqlalchemy.orm import Session
from lockana.models import Secret
from lockana.config import SECRET_KEY
from lockana.crypto import encrypt_data, decrypt_data
from lockana.exceptions import (
    ResourceNotFoundError,
    InternalServerError
)
import logging

logger = logging.getLogger(__name__)

class SecretService:
    def __init__(self, db: Session):
        self.db = db

    def list_secrets(self, username: str):
        try:
            secrets = self.db.query(Secret).filter(Secret.username == username).all()
            logger.info(f"User fetched their secrets.")
            return [
                {"name": secret.name, "data": decrypt_data(str(secret.encrypted_data), SECRET_KEY)}
                for secret in secrets
            ]
        except Exception as e:
            logger.error(f"Error listing secrets for user {username}: {str(e)}")
            raise InternalServerError(detail="Error listing secrets")

    def add_secret(self, username: str, name: str, encrypted_data: str):
        try:
            encrypted_data = encrypt_data(encrypted_data, SECRET_KEY)
            new_secret = Secret(username=username, name=name, encrypted_data=encrypted_data)
            self.db.add(new_secret)
            self.db.commit()
            logger.info(f"User added a new secret")
            return name
        except Exception as e:
            logger.error(f"Error adding secret for user {username}: {str(e)}")
            raise InternalServerError(detail="Error adding secret")

    def get_secret(self, username: str, name: str):
        try:
            secret = self.db.query(Secret).filter(Secret.username == username, Secret.name == name).first()
            if not secret:
                logger.warning(f"User tried to access a non-existing secret")
                raise ResourceNotFoundError(detail="Secret not found")
            
            logger.info(f"User accessed their secret")
            return decrypt_data(str(secret.encrypted_data), SECRET_KEY)
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting secret for user {username}: {str(e)}")
            raise InternalServerError(detail="Error getting secret")

    def update_secret(self, username: str, name: str, encrypted_data: str):
        try:
            secret = self.db.query(Secret).filter(Secret.username == username, Secret.name == name).first()
            if not secret:
                logger.warning(f"User tried to update a non-existing secret")
                raise ResourceNotFoundError(detail="Secret not found")
            
            encrypted_data = encrypt_data(encrypted_data, SECRET_KEY)
            secret.encrypted_data = encrypted_data
            self.db.commit()
            logger.info(f"User updated their secret")
            return name
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating secret for user {username}: {str(e)}")
            raise InternalServerError(detail="Error updating secret")

    def delete_secret(self, username: str, name: str):
        try:
            secret = self.db.query(Secret).filter(Secret.username == username, Secret.name == name).first()
            if not secret:
                logger.warning(f"User tried to delete a non-existing secret")
                raise ResourceNotFoundError(detail="Secret not found")
            
            self.db.delete(secret)
            self.db.commit()
            logger.info(f"User deleted their secret")
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting secret for user: {str(e)}")
            raise InternalServerError(detail="Error deleting secret") 
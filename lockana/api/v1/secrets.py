from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from lockana.api.v1.auth import oauth2_scheme, verify_token
from lockana.database.database import get_db
from lockana.models import Secret
from lockana.config import SECRET_KEY
from lockana.crypto import encrypt_data, decrypt_data
import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/secrets", tags=["Secrets"])

class SecretData(BaseModel):
    name: str
    encrypted_data: str

class SecretName(BaseModel):
    name: str

@router.get("/list")
def list_secrets(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
def add_secret(secret: SecretData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    try:
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        encrypted_data = encrypt_data(secret.encrypted_data, SECRET_KEY)
        new_secret = Secret(username=username, name=secret.name, encrypted_data=encrypted_data)
        db.add(new_secret)
        db.commit()
        logger.info(f"User {username} added a new secret: {secret.name}")
        
        return {"message": "Secret added successfully", "secret": secret.name}

    except Exception as e:
        logger.error(f"Error while adding secret for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/get")
def get_secret(secret_name: SecretName, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    try:
        name = secret_name.name
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        secret = db.query(Secret).filter(Secret.username == username, Secret.name == name).first()
        
        if not secret:
            logger.warning(f"User {username} tried to access a non-existing secret: {name}")
            raise HTTPException(status_code=404, detail="Secret not found")
        
        logger.info(f"User {username} accessed their secret: {name}")
        decrypted_data = decrypt_data(secret.encrypted_data, SECRET_KEY)
        return {"secret": decrypted_data}

    except Exception as e:
        logger.error(f"Error while retrieving secret for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/update")
def update_secret(secret: SecretData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    try:
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        secret_to_update = db.query(Secret).filter(Secret.username == username, Secret.name == secret.name).first()
        
        if not secret_to_update:
            logger.warning(f"User {username} tried to update a non-existing secret: {secret.name}")
            raise HTTPException(status_code=404, detail="Secret not found")
        
        secret_to_update.encrypted_data = encrypt_data(secret.encrypted_data, SECRET_KEY)
        db.commit()
        logger.info(f"User {username} updated their secret: {secret.name}")
        
        return {"message": "Secret updated successfully", "secret": secret.name}

    except Exception as e:
        logger.error(f"Error while updating secret for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/delete")
def delete_secret(secret_name: SecretName, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    try:
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        secret = db.query(Secret).filter(Secret.username == username, Secret.name == secret_name.name).first()

        if not secret:
            logger.warning(f"User {username} tried to delete a non-existing secret: {secret_name.name}")
            raise HTTPException(status_code=404, detail="Secret not found")

        db.delete(secret)
        db.commit()
        logger.info(f"User {username} deleted their secret: {secret_name.name}")
        
        return {"message": "Secret deleted successfully"}

    except Exception as e:
        logger.error(f"Error while deleting secret for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

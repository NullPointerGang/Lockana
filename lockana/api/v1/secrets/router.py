from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from lockana.database.database import get_db
from lockana.api.v1.auth.jwt import oauth2_scheme, verify_jwt_token
from lockana.permissions import check_permission
from .models import SecretData, SecretName
from .service import SecretService
from lockana.exceptions import (
    InvalidTokenError,
    ResourceNotFoundError,
    PermissionDeniedError,
    InternalServerError
)
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/secrets", tags=["Secrets"])

@router.get("/list")
@check_permission("read")
def list_secrets(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_jwt_token(token)
    try:
        if not username:
            raise InvalidTokenError("Invalid token")
        
        service = SecretService(db)
        secrets = service.list_secrets(username)
        return {"secrets": secrets}

    except InvalidTokenError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error while listing secrets: {str(e)}. Username: {username}")
        raise InternalServerError(detail="Internal server error while listing secrets")

@router.post("/add")
@check_permission("write")
def add_secret(secret: SecretData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_jwt_token(token)
    try:
        if not username:
            raise InvalidTokenError("Invalid token")

        service = SecretService(db)
        secret_name = service.add_secret(username, secret.name, secret.encrypted_data)
        return {"message": "Secret added successfully", "secret": secret_name}

    except InvalidTokenError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error while adding secret for user {username}: {str(e)}")
        raise InternalServerError(detail="Internal server error while adding secret")

@router.post("/get")
@check_permission("read")
def get_secret(secret_name: SecretName, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_jwt_token(token)
    try:
        if not username:
            raise InvalidTokenError("Invalid token")
        
        service = SecretService(db)
        secret_data = service.get_secret(username, secret_name.name)
        return {"secret": secret_data}

    except InvalidTokenError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except ResourceNotFoundError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error while retrieving secret for user {username}: {str(e)}")
        raise InternalServerError(detail="Internal server error while retrieving secret")

@router.put("/update")
@check_permission("write")
def update_secret(secret: SecretData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_jwt_token(token)
    try:
        if not username:
            raise InvalidTokenError("Invalid token")
        
        service = SecretService(db)
        secret_name = service.update_secret(username, secret.name, secret.encrypted_data)
        return {"message": "Secret updated successfully", "secret": secret_name}

    except InvalidTokenError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except ResourceNotFoundError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error while updating secret for user {username}: {str(e)}")
        raise InternalServerError(detail="Internal server error while updating secret")

@router.delete("/delete")
@check_permission("delete")
def delete_secret(secret_name: SecretName, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_jwt_token(token)
    try:
        if not username:
            raise InvalidTokenError("Invalid token")

        service = SecretService(db)
        service.delete_secret(username, secret_name.name)
        return {"message": "Secret deleted successfully"}

    except InvalidTokenError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except ResourceNotFoundError as e:
        return JSONResponse(content={"error": e.detail, "code": e.code}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error while deleting secret for user {username}: {str(e)}")
        raise InternalServerError(detail="Internal server error while deleting secret") 
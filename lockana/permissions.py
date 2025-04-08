from fastapi import Depends
from sqlalchemy.orm import Session
from lockana.api.v1.auth.jwt import oauth2_scheme, verify_jwt_token
from lockana.database.database import get_db
from lockana.models import User, Permission
from lockana.exceptions import (
    InvalidTokenError,
    ResourceNotFoundError,
    PermissionDeniedError
)
from functools import wraps


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    username = verify_jwt_token(token)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise InvalidTokenError("Invalid token or user not found")
    return user


def get_user_permissions(user: User, db: Session):
    if any(role.name == 'admin' for role in user.roles):
        all_permissions = db.query(Permission.name).all()
        return {perm[0] for perm in all_permissions}
    
    perms = set()
    for role in user.roles:
        perms.update({perm.name for perm in role.permissions})
    return perms

def require_permission(permission: str):
    def permission_checker(user: User = Depends(get_current_user)):
        user_permissions = get_user_permissions(user, get_db())
        if permission not in user_permissions:
            raise PermissionDeniedError("Operation not permitted for your role")
        return user
    return permission_checker

def check_permission(permission_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), **kwargs):
            username = verify_jwt_token(token)
            if not username:
                raise InvalidTokenError("Invalid token")
            
            user = db.query(User).filter(User.username == username).first()
            if not user:
                raise ResourceNotFoundError("User not found")
            
            if any(role.name == 'admin' for role in user.roles):
                return func(*args, token=token, db=db, **kwargs)
            
            user_permissions = get_user_permissions(user, db)
            
            if permission_name not in user_permissions:
                raise PermissionDeniedError("Permission denied")

            return func(*args, token=token, db=db, **kwargs)
        return wrapper
    return decorator
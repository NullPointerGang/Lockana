from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from lockana.api.v1.auth import oauth2_scheme, verify_token
from lockana.database.database import get_db
from lockana.models import User, Permission
from functools import wraps


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    username = verify_token(token)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token or user not found")
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return user
    return permission_checker

def check_permission(permission_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), **kwargs):
            username = verify_token(token)
            if not username:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user = db.query(User).filter(User.username == username).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if any(role.name == 'admin' for role in user.roles):
                return func(*args, token=token, db=db, **kwargs)
            
            user_permissions = get_user_permissions(user, db)
            
            if permission_name not in user_permissions:
                raise HTTPException(status_code=403, detail="Permission denied")

            return func(*args, token=token, db=db, **kwargs)
        return wrapper
    return decorator
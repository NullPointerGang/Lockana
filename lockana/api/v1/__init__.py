from fastapi import APIRouter
from .auth import router as auth_router
from .admin import router as admin_router
from .secrets import router as secrets_router
from .logs import router as logs_router
from .notifications import router as notifications_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(secrets_router)
api_router.include_router(logs_router)
api_router.include_router(notifications_router)

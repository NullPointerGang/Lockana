import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from lockana.api.v1 import api_router
from lockana.config import (
    APP_HOST, APP_PORT, APP_PREFIX, CORS_ENABLED, CORS_ORIGINS, CORS_METHODS, 
    CORS_HEADERS, CORS_CREDENTIALS, CORS_MAX_AGE
)
from lockana.database.database_setup import create_database_tables
from lockana import logging_config 
from lockana.error_handlers import exception_handlers

logger = logging.getLogger(__name__)

def get_base_url(request: Request) -> str:
    """Получение базового URL приложения"""
    return f"{request.base_url.scheme}://{request.base_url.netloc}"

def create_app() -> FastAPI:
    """Создание и настройка приложения FastAPI"""
    app = FastAPI(
        title="Lockana API",
        version="1.0.0"
    )

    """Настройка CORS"""
    if CORS_ENABLED:
        logger.info("CORS enabled")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=CORS_ORIGINS,
            allow_credentials=CORS_CREDENTIALS,
            allow_methods=CORS_METHODS,
            allow_headers=CORS_HEADERS,
            max_age=CORS_MAX_AGE
        )

    for exception_class, handler in exception_handlers.items():
        app.add_exception_handler(exception_class, handler)

    app.include_router(api_router, prefix=APP_PREFIX)

    @app.get("/")
    async def root(request: Request):
        """Корневой эндпоинт"""
        base_url = get_base_url(request)
        return {
            "status": "success",
            "message": "Добро пожаловать в Lockana API",
            "service": {
                "name": "Lockana",
                "version": "1.0.0",
                "description": "API для безопасного хранения и управления паролями",
                "documentation": {
                    "docs": f"{base_url}/docs",
                    "redoc": f"{base_url}/redoc",
                    "openapi": f"{base_url}/openapi.json"
                },
                "repository": {
                    "url": "https://github.com/NullPointerGang/Lockana"
                },
                "license": {
                    "name": "FOUL",
                    "url": "https://raw.githubusercontent.com/FlacSy/FOUL-LICENSE/refs/heads/main/LICENSE"
                }
            },
        }

    return app

if __name__ == '__main__':
    create_database_tables()
    app = create_app()
    logger.info("Запуск Lockana...")
    uvicorn.run(
        app, 
        host=APP_HOST, 
        port=APP_PORT
    )
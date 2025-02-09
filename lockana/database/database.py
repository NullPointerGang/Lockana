import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from lockana.models import Base
from lockana.exceptions import DatabaseException
from lockana.config import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, username: str, password: str, host: str, port: int, database_name: str, driver: str = "pymysql"):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database_name = database_name
        self.driver = driver

        self.connection_string = (
            f"mysql+{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
            "?charset=utf8mb4"
        )

        try:
            self.engine = create_engine(self.connection_string, echo=False, pool_pre_ping=True)
            Base.metadata.create_all(self.engine)
            self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
            logger.info("Подключение к базе данных успешно")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise DatabaseException(f"Ошибка базы данных: {str(e)}")

    @contextmanager
    def get_session(self) -> Session:
        """Создает и возвращает сессию базы данных"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Ошибка базы данных при работе с сессией: {e}")
            raise DatabaseException(f"Ошибка сессии: {str(e)}")
        finally:
            session.close()

    def close(self):
        """Закрывает соединение с базой данных"""
        self.engine.dispose()
        logger.info("Подключение к базе данных закрыто")

_db_instance = Database(
    username=DATABASE_USER,
    password=DATABASE_PASSWORD,
    database_name=DATABASE_NAME,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
)

def get_db():
    """Глобальный генератор сессий базы данных"""
    db = _db_instance.SessionLocal()
    try:
        return db
    finally:
        db.close()

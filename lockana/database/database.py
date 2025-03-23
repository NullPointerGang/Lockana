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
    """
    Класс для подключения и управления базой данных с использованием SQLAlchemy.

    Этот класс предоставляет методы для создания соединения с базой данных, получения сессий и выполнения операций с базой данных.
    Также реализует управление сессиями с использованием контекстного менеджера для автоматического коммита и отката.

    Атрибуты:
        username (str): Имя пользователя для подключения к базе данных.
        password (str): Пароль для подключения к базе данных.
        host (str): Хост базы данных.
        port (int): Порт базы данных.
        database_name (str): Имя базы данных.
        driver (str): Драйвер для подключения, по умолчанию 'pymysql'.

    Методы:
        __init__: Инициализирует соединение с базой данных и настраивает сессии.
        get_session: Контекстный менеджер для работы с сессиями базы данных.
        close: Закрывает соединение с базой данных.
    """
    def __init__(self, username: str, password: str, host: str, port: int, database_name: str, driver: str = "pymysql"):
        """
        Инициализирует класс для подключения к базе данных и создает все таблицы.

        Параметры:
            username (str): Имя пользователя базы данных.
            password (str): Пароль пользователя базы данных.
            host (str): Хост базы данных.
            port (int): Порт для подключения.
            database_name (str): Имя базы данных.
            driver (str): Драйвер для подключения к базе данных (по умолчанию 'pymysql').
        """
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
        """
        Контекстный менеджер для работы с сессией базы данных.

        Создает и возвращает сессию базы данных. После использования выполняется коммит,
        откат в случае ошибки, а затем сессия закрывается.

        Исключения:
            SQLAlchemyError: Ошибка при работе с базой данных во время сессии.
        """
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
        """
        Закрывает соединение с базой данных.

        Этот метод завершает соединение с базой данных и освобождает ресурсы.
        """
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
    """
    Глобальный генератор сессий для работы с базой данных.

    Возвращает новую сессию базы данных, которая автоматически закрывается после использования.

    Returns:
        db (Session): Сессия базы данных.

    Исключения:
        DatabaseException: Ошибка при создании или работе с сессией базы данных.
    """
    db = _db_instance.SessionLocal()
    try:
        return db
    finally:
        db.close()

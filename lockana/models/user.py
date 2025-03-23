from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    """
    Модель пользователя системы.

    Эта модель используется для хранения информации о пользователях, включая данные для аутентификации,
    роль пользователя и связанное состояние подключения к Telegram.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        username (str): Уникальное имя пользователя. Это поле обязательно для заполнения.
        totp_secret (str): Секрет для генерации одноразовых паролей (TOTP), используемый для двухфакторной аутентификации.
        created_at (datetime): Время создания пользователя. По умолчанию - текущее время.
        role (str): Роль пользователя в системе. По умолчанию это "user".
        telegram_connection (int): Флаг, показывающий состояние подключения к Telegram. 0 - не подключён, 1 - подключён.

    Связи:
        secrets (list of Secret): Список секретов пользователя. Связано с таблицей "secrets", где хранятся зашифрованные данные пользователя.
    
    Таблица:
        users (table): Таблица для хранения пользователей системы.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True, nullable=False)
    totp_secret = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    secrets = relationship("Secret", back_populates="user")
    role = Column(String(256), default="user")
    telegram_connection = Column(Integer, nullable=False, default=0)
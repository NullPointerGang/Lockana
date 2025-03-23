from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class Secret(Base):
    """
    Модель для хранения зашифрованных данных пользователей.

    Эта модель используется для хранения зашифрованных данных, связанных с пользователем.

    Атрибуты:
        id (int): Уникальный идентификатор записи секрета.
        username (str): Имя пользователя, которому принадлежит секрет. Ссылается на пользователя в таблице "users".
        name (str): Имя секрета. Это поле используется для идентификации секрета.
        encrypted_data (str): Зашифрованные данные секрета.
        created_at (datetime): Время создания секрета. По умолчанию - текущее время.

    Связи:
        user (User): Связь с таблицей пользователей, где у каждого секрета есть один владелец.
    
    Таблица:
        secrets (table): Таблица для хранения записей секретов пользователей.
    """
    __tablename__ = "secrets"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), ForeignKey("users.username"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    encrypted_data = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="secrets")

from sqlalchemy import Column, String, Integer, DateTime, func
from .base import Base

class Log(Base):
    """
    Модель для хранения логов действий пользователей.

    Эта модель используется для записи информации о действиях пользователей, таких как успешные и неудачные попытки входа.

    Атрибуты:
        id (int): Уникальный идентификатор записи лога.
        username (str): Имя пользователя, совершившего действие.
        action (str): Тип действия, например "LOGIN_SUCCESS" или "LOGIN_FAIL".
        timestamp (datetime): Время, когда действие было совершено. По умолчанию - текущее время.
        ip_address (str): IP-адрес пользователя, совершившего действие. Может быть пустым.

    Таблица:
        logs (table): Таблица для хранения записей логов.
    """
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    action = Column(String(255), nullable=False)  # "LOGIN_SUCCESS" | "LOGIN_FAIL"
    timestamp = Column(DateTime, default=func.now())
    ip_address = Column(String(255), nullable=True)

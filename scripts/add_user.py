from lockana.totp import TOTPManger
from lockana.database.database import _db_instance
from lockana.models.user import User
from sqlalchemy.orm import Session
from datetime import datetime


totp_manager = TOTPManger()

def add_user():
    """
    Функция для добавления нового пользователя в базу данных.

    Запрашивает информацию о пользователе (имя пользователя, секрет, роль),
    создаёт новый объект пользователя и сохраняет его в базе данных.
    Если секрет или роль не указаны, генерируются значения по умолчанию.

    Исключения:
        DatabaseException: Если происходит ошибка при добавлении пользователя в базу данных.
    """
    username = input("Username: ")
    secret = input("Secret: ")
    role = input("Role (user | admin): ")

    if not secret:
        secret = totp_manager.create_totp_secret()
    if not role:
        role = 'user'

    created_at = datetime.utcnow()
    
    new_user = User(username=username, totp_secret=secret, created_at=created_at, role=role)
    
    # Получаем сессию базы данных
    with _db_instance.get_session() as session:  # Используем сессии через контекстный менеджер
        try:
            session.add(new_user)  # Добавляем нового пользователя в сессию
            session.commit()  # Сохраняем изменения в базе данных
            print(f"User {username} added successfully!")
            print(f"Secret {secret}")
        except Exception as e:
            session.rollback()  # В случае ошибки откатываем транзакцию
            print(f"Error adding user: {e}")

if __name__ == "__main__":
    add_user()

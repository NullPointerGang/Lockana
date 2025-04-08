import questionary
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from lockana.totp import TOTPManager
from lockana.database.database import _db_instance
from lockana.models import User, Role, Permission

totp_manager = TOTPManager()

def validate_username(username: str) -> bool:
    """Валидация имени пользователя"""
    if not username:
        return False
    return 3 <= len(username) <= 32

def select_role(session) -> str:
    """Интерактивный выбор роли с автоматическим созданием базовых ролей"""
    base_roles = ["user", "admin"]
    for role_name in base_roles:
        if not session.query(Role).filter_by(name=role_name).first():
            session.add(Role(name=role_name))
    session.commit()

    existing_roles = [role.name for role in session.query(Role).all()]
    
    default_role = "user" if "user" in existing_roles else None
    
    choices = [
        questionary.Choice("Создать новую роль", value="__new__"),
        *[questionary.Choice(role, value=role) for role in existing_roles]
    ]
    
    selected = questionary.select(
        "Выберите роль пользователя:",
        choices=choices,
        default=default_role
    ).ask()
    
    if selected == "__new__":
        new_role = questionary.text(
            "Введите название новой роли:",
            validate=lambda x: "Роль уже существует!" if x in existing_roles else True
        ).ask()
        return new_role
    return selected

def handle_permissions(session, role: Role):
    """Управление разрешениями для роли"""
    if role.name == 'admin':
        all_permissions = session.query(Permission).all()
        role.permissions = all_permissions
        return
    
    permissions = session.query(Permission).all()
    selected = questionary.checkbox(
        "Выберите разрешения для роли:",
        choices=[questionary.Choice(p.name, value=p) for p in permissions]
    ).ask()
    
    role.permissions = selected

def generate_secret_interactive(username: str) -> tuple:
    """Интерактивная генерация секрета с выводом URI"""
    if questionary.confirm("Сгенерировать новый TOTP секрет?").ask():
        secret = totp_manager.create_totp_secret()
        uri = totp_manager.get_totp_uri(secret, username)
        
        try:
            import qrcode
            qr = qrcode.QRCode()
            qr.add_data(uri)
            qr.print_ascii(tty=True)
        except ImportError:
            print("Для отображения QR-кода установите библиотеку qrcode")
        
        print(f"\nСекрет: {secret}")
        print(f"URI: {uri}")
        return secret, uri
    else:
        secret = questionary.password("Введите свой секрет:").ask()
        return secret, None

def add_user_interactive():
    """Интерактивное добавление пользователя"""
    username = questionary.text(
        "Имя пользователя:",
        validate=lambda x: "Имя должно быть от 3 до 32 символов" 
        if not validate_username(x) else True
    ).ask()
    
    with _db_instance.get_session() as session:
        role_name = select_role(session)
        
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            session.add(role)
            session.commit()
            handle_permissions(session, role)
            session.commit()

        secret, uri = generate_secret_interactive(username)
        
        new_user = User(
            username=username,
            totp_secret=secret,
            created_at=datetime.utcnow(),
            roles=[role]
        )
        
        try:
            session.add(new_user)
            session.commit()
            print(f"✅ Пользователь {username} успешно добавлен!")
            print(f"Роль: {role_name}")
            print(f"Секрет: {secret}")
        except IntegrityError:
            session.rollback()
            print(f"❌ Ошибка: Пользователь {username} уже существует!")
        except Exception as e:
            session.rollback()
            print(f"❌ Критическая ошибка: {str(e)}")

def list_users():
    """Просмотр списка пользователей"""
    with _db_instance.get_session() as session:
        users = session.query(User).all()
        if not users:
            print("В системе нет пользователей")
            return
            
        print("\nСписок пользователей:")
        for user in users:
            roles = ", ".join([r.name for r in user.roles])
            print(f"• {user.username} ({roles})")

def initialize_roles_and_permissions():
    """Создает базовые роли и разрешения при первом запуске"""
    with _db_instance.get_session() as session:
        base_roles = ["user", "admin"]
        for role_name in base_roles:
            if not session.query(Role).filter_by(name=role_name).first():
                session.add(Role(name=role_name))
        
        base_permissions = ["read", "write", "delete", "manage", "logs", "logs-file", "logs-read", "logs-delete"]
        for perm_name in base_permissions:
            if not session.query(Permission).filter_by(name=perm_name).first():
                session.add(Permission(name=perm_name))
        
        session.commit()

def manage_roles():
    """Меню управления ролями"""
    while True:
        action = questionary.select(
            "Управление ролями:",
            choices=[
                questionary.Choice("Создать роль", value="create"),
                questionary.Choice("Список ролей", value="list"),
                questionary.Choice("Удалить роль", value="delete"),
                questionary.Choice("Назначить разрешения", value="perms"),
                questionary.Choice("Назад", value="back"),
            ]
        ).ask()

        if action == "back":
            break
        elif action == "create":
            create_role()
        elif action == "list":
            list_roles()
        elif action == "delete":
            delete_role()
        elif action == "perms":
            assign_permissions()

def create_role():
    """Создание новой роли"""
    with _db_instance.get_session() as session:
        role_name = questionary.text(
            "Название новой роли:",
            validate=lambda x: "Название не может быть пустым!" if not x else True
        ).ask()

        if session.query(Role).filter_by(name=role_name).first():
            print(f"❌ Роль {role_name} уже существует!")
            return

        role = Role(name=role_name)
        session.add(role)
        session.commit()
        print(f"✅ Роль {role_name} успешно создана!")
        
        if questionary.confirm("Назначить разрешения сейчас?").ask():
            assign_permissions(role_name)

def list_roles():
    """Просмотр списка ролей с разрешениями"""
    with _db_instance.get_session() as session:
        roles = session.query(Role).all()
        if not roles:
            print("В системе нет ролей")
            return
            
        print("\nСписок ролей:")
        for role in roles:
            permissions = ", ".join([p.name for p in role.permissions]) or "нет"
            print(f"• {role.name} (Разрешения: {permissions})")

def delete_role():
    """Удаление роли"""
    with _db_instance.get_session() as session:
        roles = [r.name for r in session.query(Role).all()]
        if not roles:
            print("В системе нет ролей для удаления")
            return

        role_name = questionary.select(
            "Выберите роль для удаления:",
            choices=roles
        ).ask()

        role = session.query(Role).filter_by(name=role_name).first()
        if role:
            session.delete(role)
            session.commit()
            print(f"✅ Роль {role_name} удалена!")
        else:
            print(f"❌ Роль {role_name} не найдена!")

def assign_permissions(role_name: str = None):
    """Назначение разрешений роли"""
    with _db_instance.get_session() as session:
        if not role_name:
            roles = [r.name for r in session.query(Role).all()]
            role_name = questionary.select(
                "Выберите роль:",
                choices=roles
            ).ask()

        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            print(f"❌ Роль {role_name} не найдена!")
            return

        all_permissions = session.query(Permission).all()
        if not all_permissions:
            print("❌ В системе нет доступных разрешений!")
            return

        selected = questionary.checkbox(
            f"Выберите разрешения для роли {role_name}:",
            choices=[
                questionary.Choice(
                    p.name,
                    checked=p in role.permissions,
                    value=p
                ) for p in all_permissions
            ]
        ).ask()

        role.permissions = selected
        session.commit()
        print(f"✅ Разрешения для роли {role_name} обновлены!")

def delete_user():
    """Удаление пользователя из системы"""
    with _db_instance.get_session() as session:
        users = session.query(User).all()
        if not users:
            print("В системе нет пользователей для удаления")
            return

        username = questionary.select(
            "Выберите пользователя для удаления:",
            choices=[user.username for user in users]
        ).ask()

        if not questionary.confirm(
            f"Вы уверены, что хотите удалить пользователя {username}?",
            default=False
        ).ask():
            print("❌ Удаление отменено")
            return

        user = session.query(User).filter_by(username=username).first()
        if user:
            session.delete(user)
            session.commit()
            print(f"✅ Пользователь {username} успешно удалён!")
        else:
            print(f"❌ Пользователь {username} не найден!")

def edit_user():
    """Редактирование существующего пользователя"""
    with _db_instance.get_session() as session:
        users = session.query(User).all()
        if not users:
            print("В системе нет пользователей для редактирования")
            return

        username = questionary.select(
            "Выберите пользователя для редактирования:",
            choices=[user.username for user in users]
        ).ask()

        user = session.query(User).filter_by(username=username).first()
        if not user:
            print(f"❌ Пользователь {username} не найден!")
            return

        while True:
            action = questionary.select(
                f"Редактирование пользователя {username}:",
                choices=[
                    questionary.Choice("Добавить роль", value="add_role"),
                    questionary.Choice("Удалить роль", value="remove_role"),
                    questionary.Choice("Сбросить TOTP секрет", value="reset_totp"),
                    questionary.Choice("Назад", value="back"),
                ]
            ).ask()

            if action == "back":
                break
            elif action == "add_role":
                role_name = select_role(session)
                role = session.query(Role).filter_by(name=role_name).first()
                
                if role in user.roles:
                    print(f"⚠️ Пользователь уже имеет роль {role_name}")
                    continue
                    
                user.roles.append(role)
                session.commit()
                print(f"✅ Роль {role_name} добавлена пользователю {username}")
                
            elif action == "remove_role":
                if not user.roles:
                    print("⚠️ У пользователя нет ролей для удаления")
                    continue
                
                role_to_remove = questionary.select(
                    "Выберите роль для удаления:",
                    choices=[r.name for r in user.roles]
                ).ask()
                
                role = session.query(Role).filter_by(name=role_to_remove).first()
                user.roles.remove(role)
                session.commit()
                print(f"✅ Роль {role_to_remove} удалена у пользователя {username}")
                
            elif action == "reset_totp":
                secret, uri = generate_secret_interactive(username)
                user.totp_secret = secret
                session.commit()
                print(f"✅ TOTP секрет для {username} обновлен")
                if uri:
                    print(f"Новый URI: {uri}")

def manage_users():
    """Обновлённое меню управления пользователями"""
    while True:
        action = questionary.select(
            "Управление пользователями:",
            choices=[
                questionary.Choice("Добавить пользователя", value="add"),
                questionary.Choice("Список пользователей", value="list"),
                questionary.Choice("Удалить пользователя", value="delete"),
                questionary.Choice("Редактировать пользователя", value="edit"),
                questionary.Choice("Назад", value="back"),
            ]
        ).ask()
        
        if action == "back":
            break
        elif action == "add":
            add_user_interactive()
        elif action == "list":
            list_users()
        elif action == "delete":
            delete_user()
        elif action == "edit":
            edit_user()

def main_menu():
    """Обновленное главное меню"""
    while True:
        action = questionary.select(
            "Выберите действие:",
            choices=[
                questionary.Choice("Управление пользователями", value="users"),
                questionary.Choice("Управление ролями", value="roles"),
                questionary.Choice("Выход", value="exit"),
            ]
        ).ask()
        
        if action == "users":
            manage_users()
        elif action == "roles":
            manage_roles()
        elif action == "exit":
            break


if __name__ == "__main__":
    print("🛡️ Lockana User Management CLI\n")
    initialize_roles_and_permissions() 
    main_menu()
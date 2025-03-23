import importlib
import pkgutil
import logging
from sqlalchemy.exc import SQLAlchemyError
from lockana.database.database import _db_instance
from lockana.models import Base

logger = logging.getLogger(__name__)

def import_models():
    """
    Импортирует все модели из пакета `lockana.models`.

    Эта функция динамически импортирует все модули моделей, расположенные в каталоге `lockana/models`,
    чтобы они были доступны для использования в SQLAlchemy. Функция также логирует успешный импорт каждого модуля.

    Исключения:
        - В случае ошибки импорта всех или отдельных модулей будет вызвано исключение, и ошибка будет зафиксирована в логе.
    """
    package = "lockana.models"
    
    try:
        importlib.import_module(package)
        for _, module_name, _ in pkgutil.iter_modules(["lockana/models"]):
            full_module_name = f"{package}.{module_name}"
            importlib.import_module(full_module_name)
            logger.info(f"Импортирован модуль модели: {full_module_name}")
    except Exception as e:
        logger.error(f"Ошибка при импорте моделей: {e}")
        raise

def create_tables():
    """
    Создает все таблицы в базе данных с использованием SQLAlchemy.

    Эта функция вызывает `import_models` для импорта всех моделей, а затем использует SQLAlchemy для создания всех
    таблиц, описанных в моделях, если они еще не существуют. В случае успешного создания таблиц выводится лог-сообщение.

    Исключения:
        - В случае ошибки при создании таблиц будет вызвано исключение SQLAlchemyError, и ошибка будет зафиксирована в логе.
    """
    import_models()
    
    try:
        Base.metadata.create_all(_db_instance.engine)
        logger.info("Все таблицы успешно созданы")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise

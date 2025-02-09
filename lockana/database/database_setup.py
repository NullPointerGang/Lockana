import importlib
import pkgutil
import logging
from sqlalchemy.exc import SQLAlchemyError
from lockana.database.database import _db_instance
from lockana.models import Base

logger = logging.getLogger(__name__)

def import_models():
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
    import_models()
    
    try:
        Base.metadata.create_all(_db_instance.engine)
        logger.info("Все таблицы успешно созданы")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise

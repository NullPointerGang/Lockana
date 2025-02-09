import logging
from lockana.config import LOG_FILE_NAME

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_NAME, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

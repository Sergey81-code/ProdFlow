import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

LOG_DIR_NAME = "logs"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_DIR = PROJECT_ROOT / LOG_DIR_NAME
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)

formatter = logging.Formatter("%(asctime)s | %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

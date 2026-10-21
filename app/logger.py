"""
Centralized logging configuration.
Logs go to both console and a rotating file so nothing is lost
and log files don't grow unbounded.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(settings.LOG_DIR, settings.LOG_FILE)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger. Call this in every module as:
        logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)

    if not logger.handlers:  # avoid duplicate handlers on reimport
        logger.setLevel(settings.LOG_LEVEL)

        formatter = logging.Formatter(LOG_FORMAT)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Rotating file handler: 5MB per file, keep 5 backups
        file_handler = RotatingFileHandler(
            LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

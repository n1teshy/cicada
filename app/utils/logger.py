import logging
from logging.handlers import RotatingFileHandler

from app.utils.environment import env


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%d-%m-%Y %H:%M:%S",
    )
    file_handler = RotatingFileHandler(
        env.LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    console_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

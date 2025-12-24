import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from core.config import settings

def logger():
    """
    Professional darajadagi markazlashgan logging tizimi.
    Konsolga va faylga bir vaqtda yozadi.
    """
    # Logs papkasini yaratish (agar mavjud bo'lmasa)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Logger ob'ektini yaratish
    logger = logging.getLogger("SayonarLogger")
    logger.setLevel(settings.LOG_LEVEL)

    # Formatlash: Vaqt - Ism - Daraja - Xabar
    log_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Konsol uchun handler (Rangi va ko'rinishi uchun)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # 2. Fayl uchun handler (Rotating - fayl hajmi oshib ketsa yangisini ochadi)
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,              # 5 tagacha arxiv saqlaydi
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger

# Singleton logger
logger = logger()
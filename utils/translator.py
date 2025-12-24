from typing import Dict
from core.logger import logger
from core.config import settings  # Config ni import qilamiz


class LogTranslator:
    """
    Loglarni tarjima qiluvchi klass.
    Configdagi APP_LANGUAGE ga qarab ishlaydi.
    """
    _DICTIONARY: Dict[str, str] = {
        "Smartup zip yuklab olinmoqda...": "Загрузка zip файла из Smartup...",
        "ZIP fayl muvaffaqiyatli yuklab olindi": "ZIP файл успешно загружен",
        "SFTP ga fayllar yuborilmoqda...": "Отправка файлов на SFTP...",
        "SSH ulanish muvaffaqiyatli": "SSH подключение успешно",
        "XML fayllar topilmadi": "XML файлы не найдены",
        "SUCCESS - Barcha jarayonlar muvaffaqiyatli": "УСПЕШНО - Все процессы завершены успешно",
        "ERROR - Xatolik yuz berdi:": "ОШИБКА - Произошла ошибка:",
        # Qo'shimcha so'zlar...
    }

    @classmethod
    def translate(cls, text: str) -> str:
        # AGAR TIL O'ZBEK BO'LSA - TARJIMA QILMA!
        if settings.APP_LANGUAGE == "UZB":
            return text

        if not text:
            return ""

        translated_text = text
        for uzb, rus in cls._DICTIONARY.items():
            if uzb in translated_text:
                translated_text = translated_text.replace(uzb, rus)
        return translated_text
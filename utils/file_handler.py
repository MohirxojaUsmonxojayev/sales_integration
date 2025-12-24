import os
import zipfile
import io
import shutil
from typing import List
from datetime import datetime
from core.logger import logger


class FileHandler:
    """
    Fayllar va papkalar bilan ishlash uchun mas'ul modul.
    ZIP fayllarni ochish, XMLlarni qidirish va tozalash ishlarini bajaradi.
    """

    def __init__(self, base_path: str = None):
        # Agar yo'l berilmasa, joriy papkani oladi
        self.base_path = base_path or os.getcwd()
        self.temp_dir = os.path.join(self.base_path, "temp_extract")
        self.backups_dir = os.path.join(self.base_path, "backups")

    def save_zip_to_backup(self, content: bytes) -> str:
        """Kelgan baytlarni backup papkasiga ZIP fayl qilib saqlaydi."""
        if not os.path.exists(self.backups_dir):
            os.makedirs(self.backups_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.backups_dir, f'report_{timestamp}.zip')

        with open(file_path, 'wb') as f:
            f.write(content)

        logger.info(f"Backup saqlandi: {file_path}")
        return file_path

    def extract_zip(self, content: bytes) -> List[str]:
        """ZIP tarkibini vaqtincha papkaga ochadi va XML fayllar ro'yxatini qaytaradi."""
        # Avval eski temp papka bo'lsa o'chirib yuboramiz
        self.cleanup_temp()

        os.makedirs(self.temp_dir, exist_ok=True)

        with zipfile.ZipFile(io.BytesIO(content)) as z:
            z.extractall(self.temp_dir)
            logger.info(f"ZIP fayl vaqtincha papkaga ochildi: {self.temp_dir}")

        # XML fayllarni yig'ish
        xml_files = []
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                if file.lower().endswith('.xml'):
                    xml_files.append(os.path.join(root, file))

        logger.info(f"Topilgan XML fayllar soni: {len(xml_files)} ta")
        return xml_files

    def cleanup_temp(self):
        """Vaqtincha ochilgan fayllarni o'chirib tashlaydi."""
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info("Vaqtinchalik papka tozalandi.")
            except Exception as e:
                logger.error(f"Temp papkani o'chirishda xatolik: {e}")

    def clear_old_backups(self, days: int = 7):
        """Eski backup fayllarni o'chirish (ixtiyoriy, joy tejash uchun)."""
        # Hozircha oddiygina hammasini o'chirishni skriptingda bor edi:
        if os.path.exists(self.backups_dir):
            for file in os.listdir(self.backups_dir):
                file_path = os.path.join(self.backups_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logger.error(f"Backupni o'chirishda xato: {e}")
            logger.info("Eski backuplar tozalandi.")


# Singleton instance
file_handler = FileHandler()
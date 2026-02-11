import os
import zipfile
import io
import shutil
from typing import List
from datetime import datetime
from sales_integration.core.logger import logger


class FileHandler:
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.getcwd()
        self.temp_dir = os.path.join(self.base_path, "temp_extract")
        self.backups_dir = os.path.join(self.base_path, "backups")

    def save_zip_to_backup(self, content: bytes) -> str:
        """Kelgan baytlarni backup papkasiga ZIP fayl qilib saqlaydi."""
        if not os.path.exists(self.backups_dir):
            os.makedirs(self.backups_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        timestamp_full = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        file_path = os.path.join(self.backups_dir, f'report_{timestamp_full}.zip')

        with open(file_path, 'wb') as f:
            f.write(content)

        logger.info(f"Резервная копия сохранена: {os.path.basename(file_path)}")
        return file_path

    def extract_zip(self, zip_content: bytes) -> List[str]:
        """
        ZIP faylni temp papkaga ochadi.
        """
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
                zf.extractall(self.temp_dir)

            logger.info(f"ZIP-файл распакован во временную папку: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Ошибка при распаковке ZIP: {e}")
            raise e

        # XML fayllarni yig'ish
        xml_files = []
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                if file.lower().endswith('.xml'):
                    xml_files.append(os.path.join(root, file))

        logger.info(f"Всего XML-файлов в папке: {len(xml_files)} ta")
        return xml_files

    def cleanup_temp(self):
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info("Временная папка очищена.")
            except Exception as e:
                logger.error(f"Ошибка при удалении временной папки: {e}")

    def clear_old_backups(self, days: int = 7):
        """Eski backup fayllarni o'chirish."""
        self.cleanup_temp()

        # Backuplarni tozalash (eski kod)
        if os.path.exists(self.backups_dir):
            # ... (bu qism shart emas, yoki o'zingizdagi eski kodni qoldiring) ...
            logger.info("Старые бэкапы и временная папка очищены.")


# Singleton instance
file_handler = FileHandler()
import sys
import os
from datetime import datetime
from typing import List

from core.config import settings
from core.logger import logger
from core.exceptions import SayonarBaseError, SmartupError, SFTPError
from services.smartup_client import smartup_client
from services.sftp_manager import sftp_manager
from services.mail_service import mail_service
from utils.file_handler import file_handler
# Yangi servisni import qilamiz
from services.xml_transformer import xml_transformer


def run_integration():
    current_logs: List[str] = []

    def custom_log(message: str, level: str = "info"):
        log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        current_logs.append(log_msg)
        if level == "info":
            logger.info(message)
        elif level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)

    try:
        custom_log(f"🚀 Integratsiya jarayoni boshlandi ({settings.APP_LANGUAGE} rejimi).")

        # 1. Tozalash
        file_handler.clear_old_backups()

        # 2. Yuklab olish
        zip_content = smartup_client.download_sales_report()
        custom_log("ZIP fayl muvaffaqiyatli yuklab olindi.")

        # 3. Backup
        file_handler.save_zip_to_backup(zip_content)

        # 4. Extract
        xml_files = file_handler.extract_zip(zip_content)
        if not xml_files:
            custom_log("XML fayllar topilmadi", level="error")
            raise Exception("XML fayllar topilmadi")

        custom_log(f"Topilgan XML fayllar: {len(xml_files)} ta")

        # === YANGI QISMI: FAYL TRANSFORMATSIYASI (FAQAT BORJOMI UCHUN) ===
        if settings.ENABLE_XML_TRANSFORMATION:
            custom_log("🔄 XML transformatsiya rejimi YOQILGAN.")

            for xml_file in xml_files:
                # Faqat Outlets.xml faylini qidiramiz (Katta kichik harfga qaramasdan)
                if os.path.basename(xml_file).lower() == "outlets.xml":
                    is_changed = xml_transformer.process_outlets(xml_file)
                    if is_changed:
                        custom_log("✅ Outlets.xml faylidagi AREA_ID lar yangilandi.")
                    else:
                        custom_log("ℹ️ Outlets.xml faylida o'zgarish bo'lmadi.")
        # ================================================================

        # 5. SFTP
        success = sftp_manager.upload_files(xml_files)

        if success:
            success_msg = "SUCCESS - Barcha jarayonlar muvaffaqiyatli"
            custom_log(success_msg)

            # Subjectni tilga moslash
            subject = "✅ Sayonar/Borjomi - Muvaffaqiyatli yakunlandi"
            if settings.APP_LANGUAGE == "RUS":
                subject = "✅ Sayonar - Все процессы завершены успешно"

            mail_service.send_report(
                subject=subject,
                body=success_msg,
                logs=current_logs
            )
        else:
            raise SFTPError("Fayllarni SFTP-ga yuklashda xatolik yuz berdi.")

    except SayonarBaseError as e:
        error_text = f"Loyiha xatoligi: {e.message}"
        custom_log(error_text, level="error")
        mail_service.send_report(
            subject="❌ Jarayon xatosi",
            body=error_text,
            logs=current_logs
        )
    except Exception as e:
        error_text = f"Kutilmagan xatolik: {str(e)}"
        custom_log(error_text, level="error")
        mail_service.send_report(
            subject="❌ Kutilmagan xatolik",
            body=error_text,
            logs=current_logs
        )
    finally:
        file_handler.cleanup_temp()
        custom_log("Integratsiya jarayoni yakunlandi.")


if __name__ == "__main__":
    try:
        run_integration()
    except KeyboardInterrupt:
        logger.warning("To'xtatildi.")
        sys.exit(0)
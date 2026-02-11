import sys
import os
from datetime import datetime
from typing import List

from core.config import settings
from core.logger import logger
from core.exceptions import SayonarBaseError, SFTPError
from services.smartup_client import smartup_client
from services.sftp_manager import sftp_manager
from services.ftp_manager import ftp_manager
from services.mail_service import mail_service
from utils.file_handler import file_handler
from services.xml_transformer import xml_transformer

def run_integration():
    current_logs: List[str] = []

    # Log yozish yordamchisi
    def custom_log(message: str, level: str = "info"):
        log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        current_logs.append(log_msg)

        if level == "info":
            logger.info(message)
        elif level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)

    # Bu sessiyada yaratilgan backup fayllar ro'yxati
    session_backup_files: List[str] = []

    try:
        custom_log(f"🚀 Запуск интеграции: {settings.COMPANY_NAME}")

        # 1. Tozalash (Jarayon boshida eski temp fayllarni tozalaymiz)
        file_handler.clear_old_backups()

        all_xml_files = []
        template_ids = settings.get_template_ids

        custom_log(f"Список шаблонов для обработки: {template_ids}")

        for t_id in template_ids:
            try:
                custom_log(f"📥 Скачивание шаблона ID: {t_id}...")

                # A. Yuklab olish
                zip_content = smartup_client.download_sales_report(template_id=t_id)

                # B. Backup olish (Fayl yo'lini eslab qolamiz)
                backup_path = file_handler.save_zip_to_backup(zip_content)
                session_backup_files.append(backup_path)

                # C. Extract qilish
                extracted = file_handler.extract_zip(zip_content)

                if extracted:
                    all_xml_files.extend(extracted)
                    custom_log(f"✅ Шаблон {t_id}: получено {len(extracted)} XML файлов.")
                else:
                    custom_log(f"⚠️ Шаблон {t_id}: XML файлы не найдены.", level="warning")

            except Exception as e:
                custom_log(f"❌ Ошибка с шаблоном {t_id}: {e}", level="error")

        if not all_xml_files:
            raise Exception("XML файлы не найдены ни в одном шаблоне.")

        all_xml_files = list(set(all_xml_files))
        custom_log(f"Всего файлов для отправки: {len(all_xml_files)} шт.")

        # === TRANSFORMATSIYA ===
        if settings.ENABLE_XML_TRANSFORMATION:
            custom_log("🔄 Начало: XML Трансформация (замена AREA_ID)...")
            for xml_file in all_xml_files:
                filename = os.path.basename(xml_file).lower()
                if filename == "outlets.xml":
                    try:
                        is_changed = xml_transformer.process_outlets(xml_file)
                        if is_changed:
                            custom_log(f"✅ AREA_ID обновлен: {filename}")
                        else:
                            custom_log(f"ℹ️ Без изменений: {filename}")
                    except Exception as trans_error:
                        custom_log(f"⚠️ Ошибка трансформации: {trans_error}", level="warning")

        # 3. SERVERGA YUKLASH
        protocol = getattr(settings, "PROTOCOL", "SFTP")
        custom_log(f"📤 Началась загрузка на сервер. Протокол: {protocol}")

        success = False
        if protocol == "FTP":
            success = ftp_manager.upload_files(all_xml_files)
        else:
            success = sftp_manager.upload_files(all_xml_files)

        if success:
            success_msg = f"SUCCESS - Все процессы для {settings.COMPANY_NAME} завершены успешно"
            custom_log(success_msg)

            custom_log("🗑️ Успешно завершено. Очистка файлов бэкапа...")
            for b_file in session_backup_files:
                try:
                    if os.path.exists(b_file):
                        os.remove(b_file)
                        logger.info(f"Бэкап удален: {os.path.basename(b_file)}")
                except Exception as del_err:
                    logger.warning(f"Ошибка при удалении бэкапа: {del_err}")
            # ====================================================

            subject = f"✅ {settings.COMPANY_NAME} - Все процессы завершены успешно"
            mail_service.send_report(
                subject=subject,
                body=success_msg,
                logs=current_logs
            )
        else:
            raise SFTPError(f"Ошибка при загрузке файлов на сервер ({protocol}).")

    except SayonarBaseError as e:
        error_text = f"Ошибка проекта ({settings.COMPANY_NAME}): {e.message}"
        custom_log(error_text, level="error")
        mail_service.send_report(subject=f"❌ {settings.COMPANY_NAME} - Ошибка", body=error_text, logs=current_logs)
        sys.exit(1)

    except Exception as e:
        error_text = f"Критическая ошибка ({settings.COMPANY_NAME}): {str(e)}"
        custom_log(error_text, level="error")
        mail_service.send_report(subject=f"❌ {settings.COMPANY_NAME} - Критическая ошибка", body=error_text, logs=current_logs)
        sys.exit(1)

    finally:
        # Temp (XML) fayllarni har doim tozalaymiz
        file_handler.cleanup_temp()
        custom_log("Процесс завершен.")

if __name__ == "__main__":
    run_integration()
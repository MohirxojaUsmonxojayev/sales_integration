import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List

from core.config import settings
from core.logger import logger
# MANA BU YERDA IMPORT QILISH KERAK:
from utils.translator import LogTranslator


class MailService:
    def __init__(self):
        self.sender = settings.EMAIL_SENDER
        self.password = settings.EMAIL_PASSWORD
        self.recipients = settings.recipient_list
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT

    def send_report(self, subject: str, body: str, logs: List[str] = None):
        """
        Email yuborish va loglarni tarjima qilish.
        """
        # LogTranslator yordamida tarjima qilamiz
        russian_subject = LogTranslator.translate(subject)
        russian_body = LogTranslator.translate(body)

        report_label = "ОТЧЕТ ОТ" if settings.APP_LANGUAGE == "RUS" else "HISOBOT VAQTI"
        full_content = f"{report_label}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_content += "=" * 40 + "\n"
        full_content += f"СТАТУС: {russian_body}\n"
        full_content += "=" * 40 + "\n\n"

        if logs:
            full_content += "ПОДРОБНЫЕ ЛОГИ:\n"
            # Har bir log qatorini tarjima qilamiz
            for line in logs:
                full_content += LogTranslator.translate(line) + "\n"

        for recipient in self.recipients:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.sender
                msg['To'] = recipient
                msg['Subject'] = russian_subject
                msg.attach(MIMEText(full_content, 'plain', 'utf-8'))

                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender, self.password)
                    server.send_message(msg)

                logger.info(f"Email muvaffaqiyatli yuborildi: {recipient}")
            except Exception as e:
                logger.error(f"Email yuborishda xatolik ({recipient}): {e}")


# Singleton instance
mail_service = MailService()
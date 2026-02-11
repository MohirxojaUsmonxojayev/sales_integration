import unittest
from unittest.mock import patch
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
parent_root = os.path.dirname(project_root)

sys.path.insert(0, project_root)
sys.path.insert(0, parent_root)

# Config xato bermasligi uchun
os.environ["ENV_FILE_PATH"] = os.path.join(project_root, ".env.borjomi")

# Import qilish
try:
    from services.mail_service import MailService
except ImportError:
    from sales_integration.services.mail_service import MailService


class TestMailService(unittest.TestCase):

    def setUp(self):
        self.mail_service = MailService()
        self.mail_service.sender = "test@sender.com"
        self.mail_service.password = "secretpass"
        self.mail_service.recipients = ["user1@test.com", "user2@test.com"]
        self.mail_service.smtp_server = "smtp.test.com"
        self.mail_service.smtp_port = 587

    @patch('smtplib.SMTP')
    def test_send_report_success(self, mock_smtp_class):

        mock_smtp_instance = mock_smtp_class.return_value
        mock_server = mock_smtp_instance.__enter__.return_value

        # Test ma'lumotlari
        subject = "Test Mavzu"
        body = "Hammasi joyida"
        logs = ["Log 1", "Log 2"]

        # Funksiyani chaqiramiz
        self.mail_service.send_report(subject, body, logs)

        # --- TEKSHIRUVLAR ---

        # 1. Serverga ulandimi?
        mock_smtp_class.assert_called_with("smtp.test.com", 587)

        # 2. TLS (xavfsizlik) yoqildimi?
        mock_server.starttls.assert_called()

        # 3. Login qildimi?
        mock_server.login.assert_called_with("test@sender.com", "secretpass")

        # 4. Xabar yuborildimi?
        self.assertEqual(mock_server.send_message.call_count, 2)

        print("✅ Email yuborish (Success) testi o'tdi.")

    @patch('smtplib.SMTP')
    def test_send_report_error(self, mock_smtp_class):
        """Agar SMTP server xato bersa (masalan, parol noto'g'ri)"""

        mock_smtp_instance = mock_smtp_class.return_value
        mock_server = mock_smtp_instance.__enter__.return_value

        # Xabar yuborishda xatolik chiqsin
        mock_server.send_message.side_effect = Exception("SMTP Auth Error")

        try:
            self.mail_service.send_report("Mavzu", "Matn")
        except Exception:
            self.fail("MailService xatoni ushlay olmadi! Dastur to'xtab qoldi.")

        # Login baribir chaqirilgan bo'lishi kerak
        mock_server.login.assert_called()

        print("✅ Email xatolikni ushlash (Error Handling) testi o'tdi.")

    def test_empty_recipients(self):
        """Agar qabul qiluvchilar ro'yxati bo'sh bo'lsa"""
        self.mail_service.recipients = []

        with patch('smtplib.SMTP') as mock_smtp:
            self.mail_service.send_report("Mavzu", "Matn")
            # SMTP umuman chaqirilmasligi kerak
            mock_smtp.assert_not_called()

        print("✅ Bo'sh email ro'yxati testi o'tdi.")


if __name__ == '__main__':
    unittest.main()
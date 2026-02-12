import unittest
from unittest.mock import patch
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
grandparent_root = os.path.dirname(project_root)

sys.path.insert(0, project_root)
sys.path.insert(0, grandparent_root)

os.environ["ENV_FILE_PATH"] = os.path.join(project_root, ".env.borjomi")

# Import qilish
try:
    from main import run_integration
except ImportError:
    sys.path.append(project_root)
    from main import run_integration


class TestMainIntegration(unittest.TestCase):

    @patch('main.settings')
    @patch('main.smartup_client')
    @patch('main.file_handler')
    @patch('main.sftp_manager')
    @patch('main.ftp_manager') # 5-patch
    @patch('main.mail_service')
    @patch('main.xml_transformer')
    def test_run_integration_success(self, mock_transformer, mock_mail, mock_ftp, mock_sftp, mock_file_handler,
                                     mock_smartup, mock_settings):
        """HAPPY PATH: Hamma narsa muvaffaqiyatli o'tganda."""
        # E'tibor bering: mock_ftp argumenti qo'shildi ^^^

        # 1. Sozlamalar
        mock_settings.COMPANY_NAME = "TestCompany"
        mock_settings.get_template_ids = [902, 903]
        mock_settings.ENABLE_XML_TRANSFORMATION = True
        mock_settings.PROTOCOL = "SFTP"

        # 2. Mocklar javobi
        mock_smartup.download_sales_report.return_value = b"fake_zip_bytes"
        mock_file_handler.save_zip_to_backup.return_value = "/tmp/backup.zip"
        mock_file_handler.extract_zip.return_value = ["/tmp/file1.xml", "/tmp/file2.xml"]
        mock_transformer.process_outlets.return_value = True
        mock_sftp.upload_files.return_value = True

        with patch('os.remove') as mock_remove, patch('os.path.exists', return_value=True):
            run_integration()

            # --- TEKSHIRUVLAR ---
            # Har bir template uchun o'chirish chaqiriladi (jami 2 ta)
            self.assertEqual(mock_remove.call_count, 2)
            mock_sftp.upload_files.assert_called()
            mock_mail.send_report.assert_called()

            # Argumentlarni tekshirish
            args, kwargs = mock_mail.send_report.call_args

            if args:
                subject = args[0]
            else:
                subject = kwargs.get('subject', '')

            self.assertIn("Все процессы завершены успешно", subject)

            print("✅ Main Integration (Success) testi o'tdi.")

    @patch('main.settings')
    @patch('main.smartup_client')
    @patch('main.file_handler')
    @patch('main.sftp_manager')
    @patch('main.mail_service')
    def test_run_integration_failure(self, mock_mail, mock_sftp, mock_file_handler, mock_smartup, mock_settings):
        """CRITICAL ERROR: Error Email ketadimi?"""
        mock_settings.get_template_ids = [902]
        mock_settings.PROTOCOL = "SFTP"

        mock_smartup.download_sales_report.return_value = b"zip"
        mock_file_handler.extract_zip.return_value = ["file.xml"]
        mock_sftp.upload_files.return_value = False

        with self.assertRaises(SystemExit) as cm:
            run_integration()

        self.assertEqual(cm.exception.code, 1)

        mock_mail.send_report.assert_called()

        args, kwargs = mock_mail.send_report.call_args
        if args:
            subject = args[0]
        else:
            subject = kwargs.get('subject', '')

        self.assertIn("Ошибка", subject)

        print("✅ Main Integration (Failure) testi o'tdi.")

    @patch('main.settings')
    @patch('main.smartup_client')
    @patch('main.file_handler')
    @patch('main.sftp_manager')
    @patch('main.mail_service')
    def test_partial_download_failure(self, mock_mail, mock_sftp, mock_file_handler, mock_smartup, mock_settings):
        """PARTIAL FAIL"""
        mock_settings.get_template_ids = [111, 222]
        mock_smartup.download_sales_report.side_effect = [Exception("Download Error"), b"good_zip"]

        mock_file_handler.save_zip_to_backup.return_value = "path"
        mock_file_handler.extract_zip.return_value = ["good_file.xml"]
        mock_sftp.upload_files.return_value = True

        with patch('os.remove'), patch('os.path.exists'):
            run_integration()

            mock_sftp.upload_files.assert_called()
            mock_mail.send_report.assert_called()

        print("✅ Main Integration (Partial Fail) testi o'tdi.")


if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import paramiko

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
parent_root = os.path.dirname(project_root)

sys.path.insert(0, project_root)
sys.path.insert(0, parent_root)

# Config xato bermasligi uchun
os.environ["ENV_FILE_PATH"] = os.path.join(project_root, ".env.borjomi")

# Import qilish
try:
    from services.sftp_manager import SFTPManager
except ImportError:
    from sales_integration.services.sftp_manager import SFTPManager


class TestSFTPManager(unittest.TestCase):

    def setUp(self):
        self.manager = SFTPManager()
        self.manager.host = "sftp.test.com"
        self.manager.port = 22
        self.manager.username = "user"
        self.manager.password = "pass"
        self.manager.remote_path = "/upload"

    @patch('paramiko.SSHClient')
    def test_upload_success(self, mock_ssh_class):
        """Muvaffaqiyatli yuklash testi"""

        # 1. SSH va SFTP obyektlarini soxtalashtiramiz
        mock_ssh_instance = mock_ssh_class.return_value
        mock_sftp = MagicMock()

        # open_sftp() chaqirilganda bizning soxta SFTP qaytsin
        mock_ssh_instance.open_sftp.return_value = mock_sftp

        files = ["/tmp/report.xml"]

        # Funksiyani chaqiramiz
        result = self.manager.upload_files(files)

        # --- TEKSHIRUVLAR ---
        self.assertTrue(result)

        # SSH ulanish
        mock_ssh_instance.connect.assert_called_with(
            hostname="sftp.test.com",
            port=22,
            username="user",
            password="pass",
            timeout=60,
            banner_timeout=30,
            look_for_keys=False,
            allow_agent=False,
            compress=True
        )

        # Fayl yuklash (put)
        mock_sftp.put.assert_called()
        args, _ = mock_sftp.put.call_args
        self.assertEqual(args[0], "/tmp/report.xml")  # Local path
        self.assertIn("report.xml", args[1])  # Remote path

        # Yopish
        mock_sftp.close.assert_called()
        mock_ssh_instance.close.assert_called()

        print("✅ SFTP Upload (Success) testi o'tdi.")

    @patch('paramiko.SSHClient')
    def test_connection_error_retry(self, mock_ssh_class):
        """Ulanish xatosi bo'lganda qayta urinish (Retry) ishlashi"""

        mock_ssh_instance = mock_ssh_class.return_value
        # connect() chaqirilganda xato bersin
        mock_ssh_instance.connect.side_effect = paramiko.SSHException("Connection lost")

        result = self.manager.upload_files(["file.xml"])

        # Natija False bo'lishi kerak (3 marta urinib ko'rib, oxiri to'xtaydi)
        self.assertFalse(result)

        # 3 marta urinib ko'rganini tekshiramiz
        self.assertEqual(mock_ssh_instance.connect.call_count, 3)

        print("✅ SFTP Retry (Qayta urinish) testi o'tdi.")

    @patch('paramiko.SSHClient')
    def test_auth_error(self, mock_ssh_class):
        """Login/Parol xato bo'lsa"""

        mock_ssh_instance = mock_ssh_class.return_value
        mock_ssh_instance.connect.side_effect = paramiko.AuthenticationException("Bad password")

        result = self.manager.upload_files(["file.xml"])

        self.assertFalse(result)
        print("✅ SFTP Auth Error testi o'tdi.")


if __name__ == '__main__':
    unittest.main()
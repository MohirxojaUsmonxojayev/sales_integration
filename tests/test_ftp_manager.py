import unittest
from unittest.mock import patch, mock_open
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
parent_root = os.path.dirname(project_root)

sys.path.insert(0, project_root)
sys.path.insert(0, parent_root)

os.environ["ENV_FILE_PATH"] = os.path.join(project_root, ".env.borjomi")

# Import qilish
try:
    from services.ftp_manager import FTPManager
except ImportError:
    from sales_integration.services.ftp_manager import FTPManager


class TestFTPManager(unittest.TestCase):

    def setUp(self):
        self.manager = FTPManager()
        self.manager.host = "ftp.test.com"
        self.manager.port = 21
        self.manager.username = "testuser"
        self.manager.password = "testpass"

    @patch('services.ftp_manager.FTP')
    def test_upload_success(self, mock_ftp_class):
        """Muvaffaqiyatli yuklash testi"""
        mock_ftp = mock_ftp_class.return_value
        files = ["data/report.xml"]

        with patch("builtins.open", mock_open(read_data=b"data")):
            result = self.manager.upload_files(files)

        self.assertTrue(result)
        mock_ftp.connect.assert_called_with("ftp.test.com", 21, timeout=30)
        mock_ftp.login.assert_called_with("testuser", "testpass")
        self.assertTrue(mock_ftp.storbinary.called)

        args, _ = mock_ftp.storbinary.call_args
        self.assertIn('STOR', args[0])

        mock_ftp.quit.assert_called()
        print("✅ FTP Upload (Oddiy) testi o'tdi.")

    @patch('services.ftp_manager.FTP')
    def test_connection_error(self, mock_ftp_class):
        """Ulanish xatosi testi"""
        mock_ftp = mock_ftp_class.return_value
        mock_ftp.connect.side_effect = Exception("Connection Refused")

        result = self.manager.upload_files(["file.xml"])

        self.assertFalse(result)
        print("✅ FTP Connection Error testi o'tdi.")

    @patch('services.ftp_manager.FTP')
    def test_directory_error_but_continue(self, mock_ftp_class):
        """Papka xatosi testi"""
        mock_ftp = mock_ftp_class.return_value
        mock_ftp.cwd.side_effect = Exception("Papka yo'q")
        self.manager.remote_path = "/Import"

        with patch("builtins.open", mock_open(read_data=b"data")):
            result = self.manager.upload_files(["file.xml"])

        self.assertTrue(result)
        self.assertTrue(mock_ftp.storbinary.called)
        print("✅ FTP Papka xatosi (Ignore) testi o'tdi.")

    def test_empty_files(self):
        result = self.manager.upload_files([])
        self.assertFalse(result)
        print("✅ FTP Bo'sh ro'yxat testi o'tdi.")


if __name__ == '__main__':
    unittest.main()
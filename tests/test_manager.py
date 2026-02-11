import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import subprocess

# --- YO'LLARNI TO'G'IRLASH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
grandparent_root = os.path.dirname(project_root)

sys.path.insert(0, project_root)
sys.path.insert(0, grandparent_root)

# Import manager
try:
    import manager
except ImportError:
    sys.path.append(project_root)
    import manager


class TestManager(unittest.TestCase):

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_run_client_success(self, mock_exists, mock_subprocess):
        """
        Muvaffaqiyatli ishga tushish holati.
        """
        # 1. Fayl bor deb aytamiz
        mock_exists.return_value = True

        client = {"name": "TEST_CLIENT", "env_file": ".env.test"}

        # Funksiyani chaqiramiz
        manager.run_client(client)

        # 2. subprocess.run chaqirilganini tekshiramiz
        mock_subprocess.assert_called_once()

        # 3. Argumentlarni tekshiramiz (ENV to'g'ri ketganmi?)
        args, kwargs = mock_subprocess.call_args

        # Buyruq to'g'rimi? [python, main.py]
        self.assertEqual(args[0], [sys.executable, "main.py"])

        # ENV ichida ENV_FILE_PATH bormi?
        env_vars = kwargs['env']
        self.assertEqual(env_vars['ENV_FILE_PATH'], ".env.test")

        print("✅ Manager: Muvaffaqiyatli ishga tushirish testi o'tdi.")

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_run_client_file_not_found(self, mock_exists, mock_subprocess):
        """
        Agar .env fayl yo'q bo'lsa, jarayon boshlanmasligi kerak.
        """
        # Fayl yo'q deymiz
        mock_exists.return_value = False

        client = {"name": "TEST_CLIENT", "env_file": ".env.missing"}

        manager.run_client(client)

        # Subprocess CHAQRILMASLIGI kerak
        mock_subprocess.assert_not_called()

        print("✅ Manager: Fayl yo'q bo'lsa (Skip) testi o'tdi.")

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_run_client_process_failure(self, mock_exists, mock_subprocess):
        """
        Agar main.py xato bilan tugasa (Exit code 1).
        """
        mock_exists.return_value = True

        # Subprocess xato qaytarsin
        error = subprocess.CalledProcessError(returncode=1, cmd="python main.py")
        mock_subprocess.side_effect = error

        client = {"name": "TEST_CLIENT", "env_file": ".env.test"}

        # Dastur qulamasligi kerak (try-except ishlashi kerak)
        try:
            manager.run_client(client)
        except Exception:
            self.fail("Manager xatoni ushlay olmadi!")

        print("✅ Manager: Jarayon xatoligi (Error Handling) testi o'tdi.")

    @patch('manager.run_client')
    def test_main_loop(self, mock_run_client):
        """
        Asosiy sikl (Loop) ishlashini tekshirish.
        """
        # Test uchun CLIENTS ro'yxatini vaqtincha o'zgartiramiz
        original_clients = manager.CLIENTS
        manager.CLIENTS = [
            {"name": "A", "env_file": ".env.a"},
            {"name": "B", "env_file": ".env.b"}
        ]

        manager.main()

        # 2 ta mijoz bo'lgani uchun 2 marta chaqirilishi kerak
        self.assertEqual(mock_run_client.call_count, 2)

        # Joyiga qaytaramiz
        manager.CLIENTS = original_clients
        print("✅ Manager: Asosiy sikl (Main Loop) testi o'tdi.")


if __name__ == '__main__':
    unittest.main()
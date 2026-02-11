import subprocess
import os
import sys
from datetime import datetime

CLIENTS = [
    {"name": "SAYONAR", "env_file": ".env.sayonar"},
    {"name": "BORJOMI", "env_file": ".env.borjomi"},
    {"name": "ROYALSTAR", "env_file": ".env.royalstar"},
]


def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [MANAGER] {message}")


def run_client(client):
    name = client["name"]
    env_file = client["env_file"]

    if not os.path.exists(env_file):
        log(f"❌ ОШИБКА: Файл {env_file} для {name} не найден!")
        return

    log(f"🚀 Запуск процесса {name}... (Config: {env_file})")

    # Hozirgi muhit o'zgaruvchilarini nusxalab olamiz
    env = os.environ.copy()
    # Biz config.py ga qaysi faylni o'qish kerakligini aytamiz
    env["ENV_FILE_PATH"] = env_file

    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            env=env,
            check=True,
            text=True
        )
        log(f"✅ Процесс {name} успешно завершен.")
    except subprocess.CalledProcessError as e:
        log(f"⚠️ Ошибка в процессе {name}. Cod: {e.returncode}")
    except Exception as e:
        log(f"❌ {name} не запустился: {e}")


def main():
    log("=== ЗАПУСК ИНТЕГРАЦИИ ДЛЯ ВСЕХ КЛИЕНТОВ ===")

    for client in CLIENTS:
        run_client(client)
        log("-" * 40)

    log("=== ВСЕ ЗАДАЧИ ЗАВЕРШЕНЫ ===")


if __name__ == "__main__":
    main()
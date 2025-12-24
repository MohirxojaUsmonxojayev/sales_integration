import subprocess
import os
import sys
from datetime import datetime

# Qaysi kompaniyalar uchun ishlatmoqchisan?
# Bu yerda .env fayllarining nomini yozamiz
CLIENTS = [
    {"name": "SAYONAR", "env_file": ".env.sayonar"},
    {"name": "BORJOMI", "env_file": ".env.borjomi"},
]


def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [MANAGER] {message}")


def run_client(client):
    name = client["name"]
    env_file = client["env_file"]

    if not os.path.exists(env_file):
        log(f"❌ XATOLIK: {name} uchun {env_file} fayli topilmadi!")
        return

    log(f"🚀 {name} jarayoni boshlanmoqda... (Config: {env_file})")

    # Hozirgi muhit o'zgaruvchilarini nusxalab olamiz
    env = os.environ.copy()
    # Biz config.py ga qaysi faylni o'qish kerakligini aytamiz
    env["ENV_FILE_PATH"] = env_file

    # main.py ni alohida jarayon sifatida ishga tushiramiz
    # Bu xuddi terminalda qo'lda yozgandek gap
    try:
        # python main.py
        result = subprocess.run(
            [sys.executable, "main.py"],
            env=env,
            check=True,
            text=True
        )
        log(f"✅ {name} jarayoni muvaffaqiyatli tugadi.")
    except subprocess.CalledProcessError as e:
        log(f"⚠️ {name} jarayonida xatolik yuz berdi. Kod: {e.returncode}")
    except Exception as e:
        log(f"❌ {name} ishga tushmadi: {e}")


def main():
    log("=== BARCHA MIJOZLAR UCHUN INTEGRATSIYA BOSHLANDI ===")

    for client in CLIENTS:
        run_client(client)
        log("-" * 40)

    log("=== BARCHA ISHLAR YAKUNLANDI ===")


if __name__ == "__main__":
    main()
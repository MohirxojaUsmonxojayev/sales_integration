import requests
import io
import zipfile
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from core.config import settings
from core.logger import logger


class SmartupClient:
    """
    Smartup API bilan ishlash uchun professional mijoz.
    OAuth autentifikatsiya va hisobotlarni yuklab olishni boshqaradi.
    """

    def __init__(self):
        self.base_url = settings.SMARTUP_SERVER_URL
        self.token = None

    def _get_oauth_token(self) -> str:
        """Smartup tizimidan OAuth2 access token oladi."""
        logger.info("Smartup OAuth token olinmoqda...")

        url = f"{self.base_url}/security/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": settings.SMARTUP_CLIENT_ID,
            "client_secret": settings.SMARTUP_CLIENT_SECRET,
            "scope": "read"
        }

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code != 200:
            logger.error(f"OAuth xatosi: Status {response.status_code}")
            response.raise_for_status()

        data = response.json()
        self.token = f"Bearer {data.get('access_token')}"
        logger.info("OAuth token muvaffaqiyatli olindi.")
        return self.token

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(600),  # 10 daqiqa kutish
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def download_sales_report(self) -> bytes:
        """
        Smartup-dan savdo hisobotini (ZIP) yuklab oladi.
        Xatolik yuz bersa, tenacity orqali 3 marta qayta urinadi.
        """
        if not self.token:
            self._get_oauth_token()

        logger.info("Smartup hisoboti yuklab olinmoqda...")

        url = f"{self.base_url}/trade/rep/integration/saleswork"

        # Sanalarni hisoblash
        end_date = datetime.today() - timedelta(days=1)
        begin_date = end_date - timedelta(days=settings.DAYS_DIFF)

        payload = {
            "begin_date": begin_date.strftime('%d.%m.%Y'),
            "end_date": end_date.strftime('%d.%m.%Y'),
            "period_type": settings.PERIOD_TYPE,
            "company_id": settings.COMPANY_ID,
            "filial_id": settings.FILIAL_ID,
            "template_id": settings.TEMPLATE_ID
        }

        headers = {"Authorization": self.token}

        response = requests.post(url, json=payload, headers=headers, stream=True, timeout=1800)

        if response.status_code != 200:
            logger.error(f"Hisobot yuklashda xatolik: Status {response.status_code}")
            # Agar token eskirgan bo'lsa, uni yangilash uchun tokenni o'chirib tashlaymiz
            self.token = None
            raise Exception(f"Smartup API xatosi: {response.status_code}")

        # ZIP fayl ekanligini tekshirish
        if not zipfile.is_zipfile(io.BytesIO(response.content)):
            logger.error("Yuklab olingan fayl ZIP formatida emas!")
            raise ValueError("Noto'g'ri ZIP fayl keldi")

        logger.info("ZIP fayl muvaffaqiyatli yuklab olindi.")
        return response.content


# Singleton instance
smartup_client = SmartupClient()
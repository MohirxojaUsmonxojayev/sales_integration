import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # ... (Eski Smartup, SFTP, Email sozlamalari shu yerda turadi) ...
    SMARTUP_SERVER_URL: str
    SMARTUP_CLIENT_ID: str
    SMARTUP_CLIENT_SECRET: str
    COMPANY_ID: int
    FILIAL_ID: int
    TEMPLATE_ID: int

    SFTP_SERVER: str
    SFTP_PORT: int
    SFTP_USERNAME: str
    SFTP_PASSWORD: str
    SFTP_REMOTE_PATH: str

    EMAIL_SENDER: str
    EMAIL_PASSWORD: str
    EMAIL_RECIPIENTS: str
    SMTP_SERVER: str
    SMTP_PORT: int

    PERIOD_TYPE: str = "L90D"
    DAYS_DIFF: int = 90
    LOG_LEVEL: str = "INFO"

    # === YANGI QO'SHILGAN SOZLAMALAR ===
    ENABLE_XML_TRANSFORMATION: bool = False
    APP_LANGUAGE: str = "RUS"  # Default holatda Rus tili

    @property
    def recipient_list(self) -> List[str]:
        return [email.strip() for email in self.EMAIL_RECIPIENTS.split(",")]

    # CONFIG O'ZGARISHI:
    model_config = SettingsConfigDict(
        # Atrof-muhit o'zgaruvchisidan fayl nomini oladi,
        # topa olmasa standart .env ni ishlatadi.
        env_file=os.getenv("ENV_FILE_PATH", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
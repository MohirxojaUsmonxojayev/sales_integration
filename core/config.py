import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    COMPANY_NAME: str = "Company"  # Agar .env da bo'lmasa, default "Company" bo'ladi
    SMARTUP_SERVER_URL: str
    SMARTUP_CLIENT_ID: str
    SMARTUP_CLIENT_SECRET: str
    COMPANY_ID: int
    FILIAL_ID: int
    TEMPLATE_ID: str
    PROTOCOL: str = "SFTP"


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

    ENABLE_XML_TRANSFORMATION: bool = False

    @property
    def recipient_list(self) -> List[str]:
        return [email.strip() for email in self.EMAIL_RECIPIENTS.split(",")]

    @property
    def get_template_ids(self) -> List[int]:

        if not self.TEMPLATE_ID:
            return []

        try:
            return [int(x.strip()) for x in str(self.TEMPLATE_ID).split(",")]
        except ValueError:
            # Agar kutilmagan belgi bo'lsa
            return []


    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE_PATH", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
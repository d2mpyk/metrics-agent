# config/settings.py

import base64
from typing import Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    INTERVAL_SECONDS: int = 60
    AES_SECRET_KEY: Optional[SecretStr] = None
    API_BASE_URL: str = "http://127.0.0.1:8000/api/v1"
    API_TIMEOUT: int = 10

    def get_aes_key_bytes(self) -> bytes:
        if self.AES_SECRET_KEY is None:
            raise ValueError("AES_SECRET_KEY is not set.")
        raw = base64.b64decode(self.AES_SECRET_KEY.get_secret_value())
        if len(raw) != 32:
            raise ValueError("AES key must be 32 bytes (AES-256).")
        return raw


def get_settings():
    return Settings()

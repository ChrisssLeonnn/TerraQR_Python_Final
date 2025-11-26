import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from urllib.parse import quote_plus

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database configuration
    DATABASE_URL: str

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365 * 10  # 10 years

    # Webhook settings
    VERIFY_TOKEN: str

    # Application settings
    TERRAQR_BASE_URL: str = "https://terraqr.xyz"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the DATABASE_URL is properly formatted for asyncpg
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

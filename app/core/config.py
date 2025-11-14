import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore") # Load from .env for local, ignore extra for Render

    # Database configuration
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 1433
    DB_NAME: str
    
    DATABASE_URL: str = "" # Will be constructed below

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # Application settings
    TERRAQR_BASE_URL: str = "https://terraqr.xyz"

    # Post-initialization logic
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Construct DATABASE_URL after all other DB settings are loaded
        self.DATABASE_URL = (
            f"mssql+aioodbc://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver=ODBC+Driver+18+for+SQL Server&TrustServerCertificate=yes"
        )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
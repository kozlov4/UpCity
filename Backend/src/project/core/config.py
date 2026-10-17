from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    db_url: str
    jwt_private_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    environment: str = "development"
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
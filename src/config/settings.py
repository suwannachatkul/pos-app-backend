import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends
from pydantic import AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    # Application
    ENVIRONMENT: str = "development"
    SRC_BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Database (main)
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str

    # Database (test)
    DATABASE_TEST_HOST: str = "postgres_test"
    DATABASE_TEST_PORT: int = 5432
    DATABASE_TEST_NAME: str = "app_db_test"
    DATABASE_TEST_USERNAME: str = "app_user"
    DATABASE_TEST_PASSWORD: str = "app_password"

    # JWT (for future auth)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    # Error message settings
    error_message_path: dict = {
        "en": str(
            SRC_BASE_DIR / "api" / "helpers" / "error" / "translations" / "en.json"
        ),
        "ja": str(
            SRC_BASE_DIR / "api" / "helpers" / "error" / "translations" / "ja.json"
        ),
    }

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def error_message_dict(self) -> dict:
        """Load and return error message translations from JSON files."""
        error_message_dict = {}
        for key, value in self.error_message_path.items():
            try:
                with open(value, encoding="utf-8") as f:
                    error_message_dict[key] = json.load(f)
            except FileNotFoundError:
                # Fallback to default message if file not found
                error_message_dict[key] = {"DEFAULT": "An error occurred."}
        return error_message_dict

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def test_database_url(self) -> str:
        return f"postgresql+psycopg://{self.DATABASE_TEST_USERNAME}:{self.DATABASE_TEST_PASSWORD}@{self.DATABASE_TEST_HOST}:{self.DATABASE_TEST_PORT}/{self.DATABASE_TEST_NAME}"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # ty:ignore[missing-argument]


settings: Settings = get_settings()

SettingsData = Annotated[Settings, Depends(get_settings)]

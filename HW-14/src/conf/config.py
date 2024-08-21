from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:11111111@localhost:5432/hw_13"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "admin@mail.com"
    MAIL_PASSWORD: str = "admin"
    MAIL_FROM: str = "admin@mail.com"
    MAIL_PORT: int = 5000
    MAIL_SERVER: str = "localhost"
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = "dpc5fcmq5"
    CLD_API_KEY: int = 951437173691459
    CLD_API_SECRET: str = "secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, value: Any):
        if value not in ["HS256", "HS512"]:
            raise ValueError("Invalid algorithm. Algorithm must be HS256 or HS512")
        return value

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )  # noqa

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")   # noqa


config = Settings()

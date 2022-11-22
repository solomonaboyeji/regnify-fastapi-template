"""Global Configs"""

import os
from loguru import logger
from pydantic import BaseSettings, BaseModel


def setup_logger():
    return logger


class ResponseErrorMessage(BaseModel):
    detail: str


class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "REGNIFY HTTP API")

    admin_email: str = os.getenv("ADMIN_EMAIL", "talkto@regnify.com")
    admin_first_name: str = os.getenv("ADMIN_FIRST_NAME", "Same")
    admin_last_name: str = os.getenv("ADMIN_LAST_NAME", "Doe")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "worldSecret")

    db_host: str = os.getenv("DB_HOST", None)  # type: ignore
    db_port: str = os.getenv("DB_PORT", None)  # type: ignore
    db_password: str = os.getenv("DB_PASSWORD", None)  # type: ignore
    db_name: str = os.getenv("DB_NAME", None)  # type: ignore
    db_user: str = os.getenv("DB_USER", None)  # type: ignore

    allowed_origins: list[str] = os.getenv(
        "ALLOW_ORIGINS", "http://localhost,http://localhost:8000"
    ).split(",")

    allow_origin_regex: str = os.getenv(
        "ALLOW_ORIGIN_REGEX",
        "https://.*\\.regnify\\.com|https://.*\\.azurestaticapps\\.net|https://.*\\.netlify\\.app",
    )

    doc_url: str = f"/{os.getenv('DOC_URL', 'docs')}"
    redoc_url: str = f"/{os.getenv('REDOC_URL', 'redoc')}"

    access_code_expiring_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # to get a string like this run:
    # openssl rand -hex 32
    secret_key: str = os.getenv(
        "SECRET_KEY", "d997f832a0ba79f7bc490e0cebb7b1a34c3f1ef4af1d9dd657d13ef106843166"
    )
    algorithm: str = os.getenv("ALGORITHM", "HS256")

    default_avatar_url: str = os.getenv("DEFAULT_AVATAR_URL", None)  # type: ignore

    def get_full_database_url(self):
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    def is_database_credentials_set(self):
        if (
            self.db_host is None
            or self.db_password is None
            or self.db_name is None
            or self.db_user is None
            or self.db_port is None
        ):
            return False

        return True

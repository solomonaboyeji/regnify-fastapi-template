"""Global Configs"""

import os
from loguru import logger
from pydantic import BaseSettings, BaseModel


def setup_logger():
    return logger


class ResponseErrorMessage(BaseModel):
    detail: str


class Settings(BaseSettings):
    openapi_url: str = os.getenv("OPENAPI_URL", "/openapi.json")

    app_name: str = os.getenv("APP_NAME", "REGNIFY HTTP API")
    api_version: str = os.getenv("API_VERSION", "1.0")

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

    access_code_expiring_minutes: float = float(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    password_request_minutes: float = float(
        os.getenv("PASSWORD_REQUEST_TOKEN_EXPIRE_MINUTES", "15")
    )

    # to get a string like this run:
    # openssl rand -hex 32
    secret_key: str = os.getenv(
        "SECRET_KEY", "d997f832a0ba79f7bc490e0cebb7b1a34c3f1ef4af1d9dd657d13ef106843166"
    )

    secret_key_for_tokens: str = os.getenv(
        "SECRET_KEY_FOR_TOKENS", "d997f832a0ba79f7bc490e0"
    )

    algorithm: str = os.getenv("ALGORITHM", "HS256")

    default_avatar_url: str = os.getenv("DEFAULT_AVATAR_URL", None)  # type: ignore

    admin_signup_token: str = os.getenv("ADMIN_SIGNUP_TOKEN", "not-set")  # type: ignore

    reset_password_ui_url: str = os.getenv("RESET_PASSWORD_UI_URL", "not-set")  # type: ignore
    login_ui_url: str = os.getenv("LOGIN_UI_URL", "not-set")  # type: ignore

    mail_username: str = os.getenv("MAIL_USERNAME", "not-set")  # type: ignore
    mail_password: str = os.getenv("MAIL_PASSWORD", "not-set")  # type: ignore
    mail_from: str = os.getenv("MAIL_FROM", "noreply@regnify.com")  # type: ignore
    mail_port: int = int(os.getenv("MAIL_PORT", "587"))  # type: ignore
    mail_server: str = os.getenv("MAIL_SERVER", "not-set")  # type: ignore
    mail_server: str = os.getenv("MAIL_SERVER", "not-set")  # type: ignore
    mail_starttls: bool = os.getenv("MAIL_START_TLS", "True") == "True"  # type: ignore
    mail_ssl_tls: bool = os.getenv("MAIL_SSL_TLS", "False") == "True"  # type: ignore
    use_credentials: bool = os.getenv("USE_CREDENTIALS", "False") == "True"  # type: ignore

    display_scopes: bool = os.getenv("DISPLAY_SCOPES_IN_DOCUMENTATION", "True") == "True"  # type: ignore

    cloud_sql_instance_name: str = os.getenv("CLOUD_SQL_INSTANCE_NAME", None)  # type: ignore
    sql_database_provider: str = os.getenv("SQL_DATABASE_PROVIDER", None)  # type: ignore

    minio_host: str = os.getenv("MINIO_HOST", None)  # type: ignore
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", None)  # type: ignore
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", None)  # type: ignore
    secure_minio: bool = os.getenv("SECURE_MINIO", "False") == "True"  # type: ignore

    backend_storage_option: str = os.getenv("BACKEND_STORAGE_OPTION", "MINIO_STORAGE")  # type: ignore

    # * Number of bytes to send while uploading a particular file, one at a time.
    # * If the size of a file is more than the value provided here, the value here will be used
    upload_file_bytes_per_stream: int = int(
        os.getenv("UPLOAD_FILE_BYTES_PER_STREAM", (1024 * 1024) * 100)  # 100mb
    )
    max_size_of_a_file: int = int(
        os.getenv("MAX_SIZE_OF_A_FILE", (1024 * 1024) * 100)  # 100 mb 104,857,600
    )

    def get_full_database_url(self):
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    def is_database_credentials_set(self):
        if self.sql_database_provider != "CLOUD_SQL":
            if (
                self.db_host is None
                or self.db_password is None
                or self.db_name is None
                or self.db_user is None
                or self.db_port is None
            ):
                return False
        elif self.sql_database_provider == "CLOUD_SQL":
            if (
                self.db_name is None
                or self.db_user is None
                or self.db_password is None
                or self.cloud_sql_instance_name is None
            ):
                return False
        else:
            return False

        return True

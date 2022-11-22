import pytest
from src.config import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def app_settings() -> Settings:
    return Settings()


@pytest.fixture()
def test_password() -> str:
    return "simple-password"


@pytest.fixture()
def test_super_admin_email():
    return "superAdminUser@regnify.com"


@pytest.fixture()
def test_db():
    app_settings = Settings()

    engine = create_engine(app_settings.get_full_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

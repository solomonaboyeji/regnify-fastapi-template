import pytest
from src.config import Settings
from sqlalchemy.orm import Session
from src.database import close_db_connections, get_engine, open_db_connections


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
def test_non_admin_user_email():
    return "nonAdminUser@regnify.com"


@pytest.fixture()
def test_user_without_any_roles_email():
    return "noRoleUser@regnify.com"


@pytest.fixture()
def test_db():
    open_db_connections()
    db = Session(bind=get_engine())

    try:
        yield db
    finally:
        db.close()
        close_db_connections()

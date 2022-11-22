from datetime import timedelta
from jose import jwt
from src.security import create_access_token
from src.users.crud import UserCRUD
from src.users.models import User
from src.users.schemas import UserCreate

from src.config import setup_logger

logger = setup_logger()


def test_create_access_token(app_settings):
    data = {
        "sub": "1@regnify.com",
        "is_active": True,
        "is_super_admin": False,
        "roles": [],
    }
    access_token_expires = timedelta(minutes=app_settings.access_code_expiring_minutes)
    token = create_access_token(
        data,
        expires_delta=access_token_expires,
        secret_key=app_settings.secret_key,
        algorithm=app_settings.algorithm,
    )

    payload = jwt.decode(
        token=token,
        key=app_settings.secret_key,
        algorithms=[app_settings.algorithm],
    )

    assert "sub" in payload
    assert payload["sub"] == "1@regnify.com"
    assert "is_active" in payload
    assert payload["is_active"]
    assert "is_super_admin" in payload
    assert not payload["is_super_admin"]
    assert "roles" in payload
    assert payload["roles"] == []


def test_create_user(test_db):
    email_under_test = "3@regnify.com"
    users_crud: UserCRUD = UserCRUD(db=test_db)
    user: User = users_crud.create_user(
        UserCreate(email=email_under_test, last_name="1", first_name="2", password="3")
    )
    logger.info(user.email)
    assert user.email == email_under_test

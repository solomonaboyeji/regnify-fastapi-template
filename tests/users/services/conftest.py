import pytest

from src.users.crud import UserCRUD
from src.users.models import User
from src.users.schemas import UserCreate

from src.config import Settings, setup_logger
from src.users.service import UserService

logger = setup_logger()

TEST_CACHE = {}


@pytest.fixture()
def user_service(test_db, test_user):
    user_service = UserService(
        db=test_db, requesting_user=test_user, app_settings=Settings()
    )
    return user_service


@pytest.fixture()
def test_user(test_db):
    email_under_test = "simpleUser@regnify.com"
    if email_under_test in TEST_CACHE:
        return TEST_CACHE[email_under_test]

    users_crud: UserCRUD = UserCRUD(db=test_db)
    user: User = users_crud.create_user(
        UserCreate(email=email_under_test, last_name="1", first_name="2", password="3")
    )
    logger.info(user.email)
    assert user.email == email_under_test

    TEST_CACHE[email_under_test] = user

    return user

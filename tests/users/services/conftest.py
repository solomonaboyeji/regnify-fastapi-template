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
    if "user_service" in TEST_CACHE:
        return TEST_CACHE["user_service"]

    user_service = UserService(
        db=test_db, requesting_user=test_user, app_settings=Settings()
    )

    TEST_CACHE["user_service"] = user_service

    return user_service


@pytest.fixture()
def test_user(test_db):
    email_under_test = "simpleUser@regnify.com"

    users_crud: UserCRUD = UserCRUD(db=test_db)
    if users_crud.get_user_by_email(email_under_test):
        return users_crud.get_user_by_email(email_under_test)

    user: User = users_crud.create_user(
        UserCreate(email=email_under_test, last_name="1", first_name="2", password="3")  # type: ignore
    )
    assert user.email == email_under_test
    return user


@pytest.fixture()
def test_admin_user(test_db):
    email_under_test = "simpleAdminUser@regnify.com"

    users_crud: UserCRUD = UserCRUD(db=test_db)
    if users_crud.get_user_by_email(email_under_test):
        return users_crud.get_user_by_email(email_under_test)

    user: User = users_crud.create_user(
        UserCreate(email=email_under_test, last_name="1", first_name="2", password="3"),  # type: ignore
        is_super_admin=True,
        should_make_active=True,
    )
    assert user.email == email_under_test
    return user

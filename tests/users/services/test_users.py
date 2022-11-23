from uuid import uuid4
import pytest

from src.service import ServiceResult
from src.users.exceptions import UserNotFoundException
from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate
from src.users.service import UserService

from src.config import Settings, setup_logger

logger = setup_logger()

prefix = "userTesting"


def test_create_user(user_service: UserService, test_password):
    user: ServiceResult = user_service.create_user(
        UserCreate(
            email=prefix + "1@regnify.com",
            last_name="Simple",
            first_name="User",
            password=test_password,
        )
    )

    logger.info(user.data)

    assert isinstance(user.data, User)
    assert user.data.email == prefix + "1@regnify.com"


def test_create_user_with_admin_signup_token(
    user_service: UserService, test_password: str, app_settings: Settings
):
    user_data = UserCreate(
        email=prefix + "2@regnify.com",
        last_name="Simple",
        first_name="User",
        password=test_password,
    )
    result: ServiceResult = user_service.create_user(
        user_data, admin_signup_token=app_settings.admin_signup_token
    )
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, User)
    assert result.success
    assert result.data.is_active

    # * Test Create with a wrong token
    user_data.email = "2a@regnify.com"
    result: ServiceResult = user_service.create_user(
        user_data, admin_signup_token="WRONG-TOKEN"
    )
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, User)
    assert not result.data.is_active


def test_get_user_by_email(user_service: UserService):
    # * get user with a valid email
    user_with_email = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert user_with_email.success
    assert isinstance(user_with_email.data, User)
    assert user_with_email.exception == None

    # * get user with an invalid email
    result: ServiceResult = user_service.get_user_by_email("invalid-email@regnify.com")
    assert not result.success
    assert result.data == None
    assert isinstance(result.exception, UserNotFoundException)


def test_get_user_by_id(user_service: UserService):
    # * get user with a valid email
    user = user_service.get_user_by_email(prefix + "2@regnify.com")

    user_with_id = user_service.get_user_by_id(user.data.id)
    assert user_with_id.success
    assert isinstance(user_with_id.data, User)
    assert user_with_id.exception == None

    none_result = user_service.get_user_by_id(uuid4())
    assert not none_result.success
    assert none_result.data == None
    assert isinstance(none_result.exception, UserNotFoundException)


def test_update_user(test_db, app_settings, test_admin_user):
    user_service = UserService(
        requesting_user=test_admin_user, db=test_db, app_settings=app_settings
    )
    user_under_test = user_service.get_user_by_email(prefix + "2@regnify.com")

    user_data = UserUpdate(
        is_active=False, is_super_admin=True, last_name="User22", first_name="22User"
    )
    result: ServiceResult = user_service.update_user(user_under_test.data.id, user_data)
    assert result.success
    assert isinstance(result.data, User)
    assert result.exception == None
    assert result.data.profile.first_name == "22User"
    assert result.data.profile.last_name == "User22"

    user_data = UserUpdate(last_name="User222", first_name="222User")
    result: ServiceResult = user_service.update_user(user_under_test.data.id, user_data)
    assert result.success
    assert isinstance(result.data, User)
    assert result.exception == None
    assert result.data.profile.first_name == "222User"
    assert result.data.profile.last_name == "User222"
    assert result.data.is_active == False
    assert result.data.is_super_admin

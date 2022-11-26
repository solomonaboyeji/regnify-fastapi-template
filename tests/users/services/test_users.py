import datetime
from datetime import timedelta
import time
from typing import Any

from uuid import uuid4
from jose import jwt

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


def test_update_user_last_password_token(user_service: UserService):
    service_result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(service_result, ServiceResult)
    assert isinstance(service_result.data, User)
    user_under_test: User = service_result.data

    user_service.update_user_last_password_token(user_under_test.id, "sample-code")  # type: ignore
    service_result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert service_result.data.last_password_token == "sample-code"


def test_change_password(user_service: UserService):
    service_result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(service_result, ServiceResult)
    user_under_test: User = service_result.data
    old_hashed_password = user_under_test.hashed_password
    service_result = user_service.update_user_password(user_under_test.id, "new-password")  # type: ignore
    assert isinstance(service_result, ServiceResult)
    updated_user: User = service_result.data
    assert old_hashed_password != updated_user.hashed_password

    # * try updating a user that does not exist
    service_result = user_service.update_user_password(uuid4(), "new-password")  # type: ignore
    assert not service_result.success


def test_create_request_password_token(
    user_service: UserService, app_settings: Settings
):
    result = user_service.create_request_password("invalid@regnify.com")  # type: ignore
    assert isinstance(result, ServiceResult)
    assert not result.success

    service_result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(service_result, ServiceResult)
    user_under_test: User = service_result.data

    result = user_service.create_request_password(
        user_under_test.email,  # type: ignore
    )
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, str)

    payload = jwt.decode(
        token=result.data,
        key=app_settings.secret_key_for_tokens,
        algorithms=[app_settings.algorithm],
    )
    assert payload["type"] == "PASSWORD_REQUEST"


def test_change_password_with_reset_token(
    user_service: UserService, app_settings: Settings
):
    service_result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(service_result, ServiceResult)
    user_under_test: User = service_result.data

    result = user_service.create_request_password(
        user_under_test.email,  # type: ignore
    )
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, str)

    result = user_service.change_password_with_token(result.data, "newPassword1")
    assert isinstance(result, ServiceResult)
    assert result.success


def test_should_not_be_able_change_password_with_expired_token(
    user_service: UserService, app_settings: Settings
):
    service_result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(service_result, ServiceResult)
    user_under_test: User = service_result.data

    result = user_service.create_request_password(
        user_under_test.email,  # type: ignore
    )
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, str)

    logger.debug(f"Sleeping for {app_settings.password_request_minutes * 60}")
    time.sleep(app_settings.password_request_minutes * 60)

    result = user_service.change_password_with_token(result.data, "newPassword1")
    assert isinstance(result, ServiceResult)
    assert not result.success

    # * Generate a new token and try changing password twice

    result = user_service.create_request_password(
        user_under_test.email,  # type: ignore
    )
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, str)

    # * first try would be successful
    first_try_result = user_service.change_password_with_token(
        result.data, "newPassword1"
    )
    assert isinstance(first_try_result, ServiceResult)
    assert first_try_result.success

    # * second try would not be successful
    second_try_result = user_service.change_password_with_token(
        result.data, "newPassword1"
    )
    assert isinstance(second_try_result, ServiceResult)
    assert not second_try_result.success


def test_should_not_be_able_to_change_with_invalid_user(
    user_service: UserService, app_settings
):
    expires_in = datetime.datetime.utcnow() + timedelta(
        minutes=app_settings.password_request_minutes
    )
    to_encode: dict[str, Any] = {
        "sub": str(uuid4()),
        "exp": expires_in,
        "type": "PASSWORD_REQUEST",
    }
    encoded_jwt = jwt.encode(
        to_encode,
        app_settings.secret_key_for_tokens,
        algorithm=app_settings.algorithm,
    )

    result = user_service.change_password_with_token(encoded_jwt, "newP")
    assert not result.success

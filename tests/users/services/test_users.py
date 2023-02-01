from calendar import c
import datetime
from datetime import timedelta
from io import BytesIO
import sre_parse
from sys import float_repr_style
import time
from typing import Any
from urllib import response
import uuid

from jose import jwt
from src.files.schemas import FileObjectOut

from src.service import ServiceResult
from src.users.exceptions import UserNotFoundException
from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate
from src.users.services.users import UserService

from src.config import Settings, setup_logger
from tests.files.service.test_service_files import FILE_PATH_UNDER_TEST

logger = setup_logger()

prefix = "userTesting"


def test_create_user(user_service: UserService, test_password):
    user: ServiceResult = user_service.create_user(
        UserCreate(
            email=prefix + "1@regnify.com",  # type: ignore
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
        email=prefix + "2@regnify.com",  # type: ignore
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
    user_data.email = "2a@regnify.com"  # type: ignore
    user_data.access_begin = None

    result: ServiceResult = user_service.create_user(
        user_data, admin_signup_token="WRONG-TOKEN"
    )
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, User)
    assert not result.data.is_active


def test_create_users_with_access_period(
    user_service: UserService, test_password: str, app_settings: Settings
):
    access_end = datetime.datetime.now()
    access_begin = datetime.datetime.now() - timedelta(days=1)

    user_data = UserCreate(
        email=prefix + "2.a@regnify.com",  # type: ignore
        last_name="Simple",
        first_name="User",
        password=test_password,
        access_begin=access_begin,
        access_end=access_end,
    )
    result: ServiceResult = user_service.create_user(
        user_data, admin_signup_token=app_settings.admin_signup_token
    )
    assert isinstance(result, ServiceResult)
    assert result.data.access_end == access_end
    assert result.data.access_begin == access_begin

    # * create without access end or begin
    user_data = UserCreate(
        email=prefix + "2.a.1@regnify.com",  # type: ignore
        last_name="Simple",
        first_name="User",
        password=test_password,
    )
    result: ServiceResult = user_service.create_user(
        user_data, admin_signup_token=app_settings.admin_signup_token
    )
    assert isinstance(result, ServiceResult)
    # * the access begin must start from the time the user was created
    assert result.data.access_begin != None
    assert result.data.access_end == None


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

    none_result = user_service.get_user_by_id(uuid.uuid4())
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


def test_upload_user_photo(test_db, app_settings, test_admin_user, test_password):

    user_service = UserService(
        requesting_user=test_admin_user, db=test_db, app_settings=app_settings
    )

    result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, User)
    user_under_test: User = result.data

    with open(FILE_PATH_UNDER_TEST, "rb") as f:
        result = user_service.upload_user_photo(
            user_id=uuid.UUID(str(user_under_test.id)),
            buffer=f,
            file_name="simple-file.png",
        )
        assert result.success, result.exception
        assert result.data.photo_file != None
        assert result.data.photo_file.original_file_name == "simple-file.png"

    # * Test the download of the photo file
    result = user_service.download_user_photo(
        user_id=uuid.UUID(str(user_under_test.id))
    )
    assert result.success, result.exception

    assert isinstance(result.data[0], BytesIO)
    assert isinstance(result.data[1], FileObjectOut)
    assert len(result.data[0].read()) > 0


def test_non_admin_cannot_upload_photo_for_another_user(
    test_db, app_settings, test_admin_user, test_password
):

    user_service = UserService(
        requesting_user=test_admin_user, db=test_db, app_settings=app_settings
    )

    result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, User)
    user_under_test: User = result.data

    # * create non admin user
    non_admin_user: ServiceResult = user_service.create_user(
        UserCreate(
            email=prefix + "1-1-new-user@regnify.com",  # type: ignore
            last_name="Simple",
            first_name="User",
            password=test_password,
        )
    )
    assert isinstance(non_admin_user.data, User)
    non_admin_user = non_admin_user.data

    # * create user service with the non admin user as the requesting user.
    non_admin_user_service = UserService(
        requesting_user=non_admin_user, db=test_db, app_settings=app_settings
    )

    with open(FILE_PATH_UNDER_TEST, "rb") as f:
        result = non_admin_user_service.upload_user_photo(
            user_id=uuid.UUID(str(user_under_test.id)),
            buffer=f,
            file_name="simple-file.png",
        )
        assert not result.success, result.exception


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
    assert old_hashed_password != updated_user.hashed_password  # type: ignore

    # * try updating a user that does not exist
    service_result = user_service.update_user_password(uuid.uuid4(), "new-password")  # type: ignore
    assert not service_result.success


def test_create_request_password_token(
    test_db, test_user: User, app_settings: Settings
):
    user_service = UserService(
        db=test_db, requesting_user=test_user, app_settings=Settings()
    )

    result = user_service.create_request_password("invalid@regnify.com")  # type: ignore
    assert isinstance(result, ServiceResult)
    assert not result.success

    service_result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(service_result, ServiceResult)
    assert service_result.success, service_result.exception
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


def test_change_password_with_reset_token(test_db, test_user: User):
    user_service = UserService(
        db=test_db, requesting_user=test_user, app_settings=Settings()
    )
    service_result = user_service.get_user_by_email(prefix + "2@regnify.com")
    assert isinstance(service_result, ServiceResult)
    assert service_result.success, service_result.exception
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
    assert service_result.success, service_result.exception
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
        "sub": str(10000000),
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

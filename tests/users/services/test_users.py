from src.service import ServiceResult
from src.users.models import User
from src.users.schemas import UserCreate
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

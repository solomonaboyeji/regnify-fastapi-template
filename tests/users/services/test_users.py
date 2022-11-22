from src.service import ServiceResult
from src.users.models import User
from src.users.schemas import UserCreate
from src.users.service import UserService

from src.config import setup_logger

logger = setup_logger()

prefix = "userTesting"


def test_create_user(test_db, test_user: User, test_password: str):
    user_service = UserService(db=test_db, requesting_user=test_user)
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

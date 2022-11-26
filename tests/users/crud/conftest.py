import pytest
from src.config import Settings
from src.database import get_db
from src.exceptions import GeneralException

from src.users.crud import UserCRUD
from src.users.models import User


@pytest.fixture()
def user_crud(test_db):
    return UserCRUD(db=test_db)


@pytest.fixture()
def role_crud(test_db):
    return RoleCRUD(db=test_db)


@pytest.fixture()
def crud_user_email():
    return "crud_user@regnify.com"


@pytest.fixture()
def crud_user(test_db, crud_user_email) -> User:
    users_crud: UserCRUD = UserCRUD(db=test_db)
    try:
        user: User = users_crud.create_user(
            UserCreate(email=email_under_test, last_name="1", first_name="2", password="3")  # type: ignore
        )
    except GeneralException:
        user: User = users_crud.get_user_by_email(crud_user_email)

    return user

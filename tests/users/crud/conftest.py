from sqlite3 import IntegrityError
import pytest
from src.exceptions import GeneralException
from src.users.crud.roles import RoleCRUD

from src.users.crud.users import UserCRUD
from src.users.models import User
from src.users.schemas import UserCreate


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
def crud_user_email_2():
    return "crud_user_2@regnify.com"


@pytest.fixture()
def crud_user(test_db, crud_user_email) -> User:
    users_crud: UserCRUD = UserCRUD(db=test_db)
    user: User = users_crud.get_user_by_email(crud_user_email)
    if not user:
        user: User = users_crud.create_user(
            UserCreate(email=crud_user_email, last_name="1", first_name="2", password="3")  # type: ignore
        )
    return user


@pytest.fixture()
def crud_user_2(test_db, crud_user_email_2) -> User:
    users_crud: UserCRUD = UserCRUD(db=test_db)
    user: User = users_crud.get_user_by_email(crud_user_email_2)
    if not user:
        user: User = users_crud.create_user(
            UserCreate(email=crud_user_email_2, last_name="1", first_name="2", password="3")  # type: ignore
        )
    return user

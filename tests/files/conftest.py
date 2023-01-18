import pytest

from src.users.crud.users import UserCRUD
from src.users.models import User
from src.users.schemas import UserCreate

email_under_test = "simple-filer@regnify.com"


@pytest.fixture()
def file_user(test_db):
    users_crud: UserCRUD = UserCRUD(db=test_db)
    user: User = users_crud.get_user_by_email(email_under_test)
    if not user:
        user: User = users_crud.create_user(
            UserCreate(email=email_under_test, last_name="Filer", first_name="James", password="332244")  # type: ignore
        )
    return user

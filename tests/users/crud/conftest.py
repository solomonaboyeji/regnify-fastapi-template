import pytest

from src.users.crud import UserCRUD


@pytest.fixture()
def user_crud(test_db):
    return UserCRUD(db=test_db)

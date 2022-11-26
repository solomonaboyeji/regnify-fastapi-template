import pytest

from src.config import setup_logger
from src.users.crud import UserCRUD
from src.users.models import User, UserScope

logger = setup_logger()


def test_create_role(test_db, crud_user: User):
    roles_crud: RoleCRUD = RoleCRUD(db=test_db)
    roles_crud.create_role(
        title="Role 1",
        permissions=[UserScope.READ, UserScope.WRITE, UserScope.VIEW, UserScope.DELETE],
        created_by=crud_user,
    )

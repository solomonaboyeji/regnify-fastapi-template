import enum
from uuid import UUID

from src.pagination import OrderBy, OrderDirection
from src.scopes import UserScope
from src.users.crud.roles import RoleCRUD
from src.users.models import Roles, User


def create_test_role(
    role_crud: RoleCRUD,
    crud_user: User,
    title: str = None,  # type: ignore
    permissions_scopes: list = [
        UserScope.READ.value,
        UserScope.CREATE.value,
        UserScope.UPDATE.value,
        UserScope.DELETE.value,
    ],
):  # type: ignore
    role_created = role_crud.create_role(
        title=title,
        permissions=permissions_scopes,
        created_by=crud_user,
    )

    assert isinstance(role_created, Roles)
    for permission_scope in permissions_scopes:
        if isinstance(permission_scope, enum.Enum):
            assert permission_scope.value in role_created.permissions
        else:
            assert permission_scope in role_created.permissions

    assert role_created.created_by == crud_user.id
    return role_created


def get_test_first_role(role_crud: RoleCRUD, user: User):
    created_roles = role_crud.get_roles(
        start=0,
        limit=1,
        user_id=UUID(str(user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    role_under_test = created_roles[0]

    role = role_crud.get_role(role_id=role_under_test.id)  # type: ignore

    return role


# * End Utils

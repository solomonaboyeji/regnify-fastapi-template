import pytest
from uuid import UUID, uuid4

from src.config import setup_logger
from src.exceptions import BaseConflictException, BaseNotFoundException
from src.pagination import OrderBy, OrderDirection
from src.scopes import UserScope
from src.users.crud.roles import RoleCRUD
from src.users.crud.users import UserCRUD
from src.users.models import Roles, User, UserRoles
from tests.common.users import create_test_role, get_test_first_role

logger = setup_logger()

CUSTOM_ROLE_TITLE = "Custom Role"


# * Utils


def test_create_role(role_crud: RoleCRUD, crud_user: User):
    create_test_role(role_crud, crud_user, title=CUSTOM_ROLE_TITLE)
    create_test_role(role_crud, crud_user, title=f"{CUSTOM_ROLE_TITLE} 2")


def test_get_roles_with_pagination(
    role_crud: RoleCRUD, crud_user: User, crud_user_2: User
):

    created_roles = role_crud.get_roles(
        start=0,
        limit=10,
        user_id=UUID(str(crud_user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    assert isinstance(created_roles, list)

    # * Test DESC Ordering
    previous_date = None
    for role in created_roles:
        if not previous_date:
            previous_date = role.date_created

        assert previous_date >= role.date_created

    # * Test ASC Ordering
    created_roles_in_asc = role_crud.get_roles(
        start=0,
        limit=10,
        user_id=UUID(str(crud_user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.ASC,
    )
    previous_date = None
    for role in created_roles_in_asc:
        if not previous_date:
            previous_date = role.date_created

        assert previous_date <= role.date_created

    # * Test start, limit
    created_roles = role_crud.get_roles(
        start=0,
        limit=1,
        user_id=UUID(str(crud_user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    assert len(created_roles) == 1

    created_roles = role_crud.get_roles(
        start=100,
        limit=10,
        user_id=UUID(str(crud_user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    assert len(created_roles) == 0

    # * User 2 can also access the roles
    created_roles = role_crud.get_roles(
        start=0,
        limit=10,
        user_id=UUID(str(crud_user_2.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    assert len(created_roles) == 2


def test_get_role(role_crud: RoleCRUD, crud_user: User):
    created_roles = role_crud.get_roles(
        start=0,
        limit=1,
        user_id=UUID(str(crud_user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    role_under_test = created_roles[0]

    role = role_crud.get_role(role_id=role_under_test.id)  # type: ignore
    assert isinstance(role, Roles)
    assert role_under_test == role


def test_get_roles_with_search(role_crud: RoleCRUD, crud_user: User):
    # * Test searching for the first few indexes
    created_roles = role_crud.get_roles(
        start=0,
        limit=10,
        title=CUSTOM_ROLE_TITLE[0:4],
        user_id=UUID(str(crud_user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    assert isinstance(created_roles, list)
    assert len(created_roles) == 2

    # * Test searching for a full string
    created_roles = role_crud.get_roles(
        start=0,
        limit=1,
        title=CUSTOM_ROLE_TITLE + " 2",
        user_id=UUID(str(crud_user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    assert isinstance(created_roles, list)
    assert len(created_roles) == 1


def test_edit_role(role_crud: RoleCRUD, crud_user: User):
    title = CUSTOM_ROLE_TITLE + "12"
    created_roles = role_crud.get_roles(
        start=0,
        limit=1,
        user_id=UUID(str(crud_user.id)),
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    role_under_test = created_roles[0]

    role = role_crud.get_role(role_id=role_under_test.id)  # type: ignore
    assert isinstance(role, Roles)
    assert role_under_test == role

    updated_role = role_crud.update_role(
        role_id=role_under_test.id,  # type: ignore
        title=title,
        permissions=[UserScope.DELETE.value],
        updated_by=crud_user,  # type: ignore
    )

    assert isinstance(updated_role, Roles)
    assert updated_role.title == title.lower()
    assert updated_role.permissions == [UserScope.DELETE.value]
    assert updated_role.modified_by == crud_user.id

    updated_role = role_crud.update_role(
        role_id=role_under_test.id,  # type: ignore
        title=title,
        permissions=[UserScope.DELETE.value],
        updated_by=crud_user,  # type: ignore
    )


def test_edit_role_with_duplicate(role_crud: RoleCRUD, crud_user: User):
    title = CUSTOM_ROLE_TITLE + "12"
    new_role = create_test_role(role_crud, crud_user, title=f"{CUSTOM_ROLE_TITLE} 3")
    with pytest.raises(BaseConflictException):
        role_crud.update_role(
            role_id=new_role.id,  # type: ignore
            title=title,
            permissions=[UserScope.DELETE.value],
            updated_by=crud_user,  # type: ignore
        )


def test_edit_role_not_found(role_crud: RoleCRUD, crud_user: User):
    with pytest.raises(BaseNotFoundException):
        role_crud.update_role(
            role_id=uuid4(),  # type: ignore
            title="title",
            permissions=[UserScope.DELETE.value],
            updated_by=crud_user,  # type: ignore
        )


def test_a_user_cannot_create_two_roles_with_same_title(
    role_crud: RoleCRUD, crud_user: User
):
    role = get_test_first_role(role_crud, crud_user)
    with pytest.raises(BaseConflictException):
        role_crud.create_role(
            role.title, permissions=[UserScope.DELETE.value], created_by=crud_user  # type: ignore
        )


def test_assign_role_to_a_user(
    role_crud: RoleCRUD, crud_user: User, user_crud: UserCRUD
):
    role_to_assign = get_test_first_role(role_crud, crud_user)
    user_role: UserRoles = role_crud.assign_role(crud_user, role_to_assign)
    assert user_role.role_id == role_to_assign.id  # type: ignore
    assert crud_user.id == crud_user.id  # type: ignore
    assert len(crud_user.user_roles) > 0
    assert crud_user.user_roles[0].role_id == role_to_assign.id  # type: ignore

    assert len(user_crud.get_user(crud_user.id).user_roles) > 0  # type: ignore

    with pytest.raises(BaseConflictException):
        user_role: UserRoles = role_crud.assign_role(crud_user, role_to_assign)


def test_get_user_assigned_to_roles(role_crud: RoleCRUD, crud_user: User):
    role_to_assign = get_test_first_role(role_crud, crud_user)

    users = role_crud.get_user_assigned_to_roles(role_to_assign.id)  # type: ignore
    assert len(users) > 0

    assert role_crud.get_total_user_assigned_to_role(role_id=role_to_assign.id) == len(  # type: ignore
        users
    )


def test_unassign_role_to_a_user(role_crud: RoleCRUD, crud_user: User):
    initial_total_roles = len(crud_user.user_roles)
    role_to_assign = get_test_first_role(role_crud, crud_user)
    role_crud.unassign_role(crud_user.id, role_to_assign.id)  # type: ignore
    assert len(crud_user.user_roles) < initial_total_roles
    assert role_to_assign.id not in crud_user.user_roles  # type: ignore

    with pytest.raises(BaseNotFoundException):
        role_crud.unassign_role(crud_user.id, role_to_assign.id)  # type: ignore


# delete role unassign role from users
def test_delete_role_unassign_user_from_the_role(role_crud: RoleCRUD, crud_user: User):
    role_to_assign = get_test_first_role(role_crud, crud_user)
    role_crud.assign_role(crud_user, role_to_assign)
    role_crud.delete_role(role_to_assign.id)  # type: ignore
    assert role_to_assign.id not in crud_user.user_roles  # type: ignore

    with pytest.raises(BaseNotFoundException):
        role_crud.delete_role(role_to_assign.id)  # type: ignore

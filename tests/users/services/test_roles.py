from uuid import uuid4
from src.config import Settings
from src.pagination import OrderBy, OrderDirection
from src.scopes import UserScope
from src.service import ServiceResult
from src.users.schemas import ManyRolesOut, RoleCreate, RoleOut
from src.users.services.roles import RolesService
from src.users.services.users import UserService

prefix = "troles"
CUSTOM_ROLE_NAME = f"{prefix}Custom Role"

# * utils
def get_test_all_roles(db, user):
    role_service = RolesService(db=db, app_settings=Settings(), requesting_user=user)
    result = role_service.get_roles(
        start=0,
        limit=10,
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    assert isinstance(result, ServiceResult)
    assert result.success
    assert isinstance(result.data, ManyRolesOut)
    assert result.data.total > 0
    assert isinstance(result.data.roles, list)

    return result.data.roles


def test_create_role(role_service: RolesService):
    role_result = role_service.create_role(
        RoleCreate(title=CUSTOM_ROLE_NAME, permissions=[UserScope.DELETE.value])
    )
    assert isinstance(role_result, ServiceResult)
    print(role_result.exception)
    assert role_result.success
    assert role_result.data.title == CUSTOM_ROLE_NAME.lower()

    role_name = CUSTOM_ROLE_NAME + " 2"
    role_result = role_service.create_role(
        RoleCreate(
            title=role_name, permissions=[UserScope.DELETE.value, UserScope.READ.value]
        )
    )
    assert isinstance(role_result, ServiceResult)
    assert role_result.success
    assert role_result.data.title == role_name.lower()


def test_get_all_roles(test_db, test_user):
    role_service = RolesService(
        db=test_db, app_settings=Settings(), requesting_user=test_user
    )
    result = role_service.get_roles(
        start=0,
        limit=10,
        order_by=OrderBy.DATE_CREATED,
        order_direction=OrderDirection.DESC,
    )
    assert isinstance(result, ServiceResult)
    assert result.success
    assert isinstance(result.data, ManyRolesOut)
    assert result.data.total > 0
    assert isinstance(result.data.roles, list)


def test_get_single_role(test_db, test_user, role_service: RolesService):
    roles = get_test_all_roles(test_db, test_user)
    result = role_service.get_role(roles[0].id)

    assert isinstance(result, ServiceResult)
    assert result.success

    # * get a role that does not exist
    roles = get_test_all_roles(test_db, test_user)
    result = role_service.get_role(uuid4())

    assert isinstance(result, ServiceResult)
    assert not result.success


def test_edit_role(test_db, test_user):
    role_service = RolesService(
        db=test_db, app_settings=Settings(), requesting_user=test_user
    )
    roles = get_test_all_roles(test_db, test_user)
    result = role_service.get_role(roles[0].id)

    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, RoleOut)
    role = result.data

    edited_result = role_service.update_role(
        role.id, title=role.title, permissions=role.permissions
    )
    assert isinstance(edited_result, ServiceResult)

    result = role_service.get_role(roles[0].id)
    assert isinstance(result, ServiceResult)
    assert isinstance(result.data, RoleOut)
    assert result.data.title == edited_result.data.title


def test_cannot_create_duplicate_role(test_db, test_user):
    role_service = RolesService(
        db=test_db, app_settings=Settings(), requesting_user=test_user
    )
    role_result = role_service.create_role(
        RoleCreate(title=CUSTOM_ROLE_NAME, permissions=[UserScope.DELETE.value])
    )
    assert isinstance(role_result, ServiceResult)
    assert not role_result.success


def test_cannot_update_duplicate_role(test_db, test_user):
    role_service = RolesService(
        db=test_db, app_settings=Settings(), requesting_user=test_user
    )
    roles = get_test_all_roles(test_db, test_user)
    assert len(roles) > 1
    role = roles[0]
    second_role = roles[1]
    edited_result = role_service.update_role(
        role.id, title=second_role.title, permissions=second_role.permissions
    )
    assert isinstance(edited_result, ServiceResult)
    assert not edited_result.success


def test_assign_role(test_db, test_user, role_service: RolesService):
    roles = get_test_all_roles(test_db, test_user)
    role = roles[0]
    assert isinstance(role, RoleOut)
    result = role_service.assign_role(role.id, test_user.id)
    assert isinstance(result, ServiceResult)
    assert result.success
    assert len(result.data.user_roles) > 0


def test_get_user_assigned_to_roles(test_db, test_user, role_service: RolesService):
    roles = get_test_all_roles(test_db, test_user)
    role = roles[0]
    assert isinstance(role, RoleOut)
    result = role_service.get_users_assigned_to_role(role_id=role.id)
    assert isinstance(result, ServiceResult)
    assert result.data.total == 1
    assert len(result.data.user_roles) == 1


def test_unassign_role(test_db, test_user):
    role_service = RolesService(
        requesting_user=test_user, db=test_db, app_settings=Settings()
    )
    user_service = UserService(
        requesting_user=test_user, db=test_db, app_settings=Settings()
    )

    result = user_service.get_user_by_id(test_user.id)
    assert isinstance(result, ServiceResult)
    assert result.success
    assert len(result.data.user_roles) > 0

    role_to_remove = result.data.user_roles[0]
    user_data = role_service.unassign_role(role_to_remove.role_id, test_user.id)
    assert user_data.success

    result = user_service.get_user_by_id(test_user.id)
    assert isinstance(result, ServiceResult)
    assert result.success
    assert len(result.data.user_roles) == 0


def test_delete_role_unassigns_role(test_db, test_user):
    role_service = RolesService(
        requesting_user=test_user, db=test_db, app_settings=Settings()
    )
    user_service = UserService(
        requesting_user=test_user, db=test_db, app_settings=Settings()
    )

    roles = get_test_all_roles(test_db, test_user)
    role = roles[0]
    assert isinstance(role, RoleOut)

    # * assign the user the role
    result = role_service.assign_role(role.id, test_user.id)
    assert isinstance(result, ServiceResult)

    # * delete the role
    delete_result = role_service.delete_role(role.id)
    assert delete_result.success

    # * the role must have been removed from the user as well.
    result = user_service.get_user_by_id(test_user.id)
    assert isinstance(result, ServiceResult)
    assert result.success
    assert len(result.data.user_roles) == 0

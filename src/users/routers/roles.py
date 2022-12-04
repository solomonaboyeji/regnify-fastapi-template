"""User's Router"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Security, Body
from src.config import setup_logger
from src.scopes import RoleScope
from src.pagination import CommonQueryParams, OrderBy, OrderDirection
from src.service import AppResponseModel, handle_result
from src.users import schemas
from src.users.dependencies import (
    initiate_role_service,
)
from src.users.services.roles import RolesService

router = APIRouter(tags=["Roles and Permissions"], prefix="/roles")


logger = setup_logger()


@router.post(
    "/",
    response_model=schemas.RoleOut,
)
def create_role(
    data: schemas.RoleCreate,
    role_service: RolesService = Security(
        initiate_role_service, scopes=[RoleScope.CREATE.value]
    ),
):
    """Allows an admin to create a role in the system."""

    result = role_service.create_role(role_data=data)
    return handle_result(result, schemas.RoleOut)  # type: ignore


@router.get(
    "/",
    response_model=schemas.ManyRolesOut,
)
def get_roles(
    commons: CommonQueryParams = Depends(),
    order_by: OrderBy = OrderBy.DATE_CREATED,
    order_direction: OrderDirection = OrderDirection.DESC,
    title: str = None,  # type: ignore
    role_service: RolesService = Security(
        initiate_role_service, scopes=[RoleScope.READ.value]
    ),
):
    """Gets all the roles in the system"""

    result = role_service.get_roles(
        start=commons.skip,
        limit=commons.limit,
        title=title,
        order_by=order_by,
        order_direction=order_direction,
    )
    return handle_result(result, schemas.ManyRolesOut)  # type: ignore


@router.get(
    "/{role_id}",
    response_model=schemas.RoleOut,
)
def get_role(
    role_id: UUID,
    role_service: RolesService = Security(
        initiate_role_service, scopes=[RoleScope.READ.value]
    ),
):
    """Gets a single role"""
    result = role_service.get_role(role_id=role_id)
    return handle_result(result, schemas.RoleOut)  # type: ignore


@router.put(
    "/{role_id}",
    response_model=schemas.RoleOut,
)
def edit_role(
    role_id: UUID,
    title: str = Body(),
    permissions: list[str] = Body(),
    role_service: RolesService = Security(
        initiate_role_service, scopes=[RoleScope.UPDATE.value]
    ),
):
    """Updates a single role"""
    result = role_service.update_role(
        role_id=role_id, title=title, permissions=permissions
    )
    return handle_result(result, schemas.RoleOut)  # type: ignore


@router.post(
    "/{role_id}/assign-role",
    response_model=schemas.UserOut,
)
def assign_role(
    user_id: UUID,
    role_id: UUID,
    role_service: RolesService = Security(
        initiate_role_service, scopes=[RoleScope.CREATE.value]
    ),
):
    """Assigns the role to the specified user."""

    result = role_service.assign_role(role_id, user_id)
    return handle_result(result, schemas.UserOut)  # type: ignore


@router.post(
    "/{role_id}/unassign-role",
    response_model=schemas.UserOut,
)
def unassign_role(
    user_id: UUID,
    role_id: UUID,
    role_service: RolesService = Security(
        initiate_role_service, scopes=[RoleScope.CREATE.value]
    ),
):
    """Unassign the role to the specified user."""

    result = role_service.unassign_role(role_id, user_id)
    return handle_result(result, schemas.UserOut)  # type: ignore


@router.delete(
    "/{role_id}",
    response_model=AppResponseModel,
)
def delete_role(
    role_id: UUID,
    role_service: RolesService = Security(
        initiate_role_service, scopes=[RoleScope.CREATE.value]
    ),
):
    """Deletes the role. This endpoint removes the roles from all users that has been previously assigned. The integer returned is the total number of all users the role has been removed from."""

    result = role_service.delete_role(role_id)
    return handle_result(result)  # type: ignore


@router.get(
    "/{role_id}/list-assigned-users",
    response_model=schemas.ManyUserRolesOut,
)
def list_users_assigned_to_role(
    role_id: UUID,
    role_service: RolesService = Security(
        initiate_role_service, scopes=[RoleScope.READ.value]
    ),
):
    """List the users that are assigned to a particular role."""

    result = role_service.get_users_assigned_to_role(role_id)
    return handle_result(result, schemas.ManyUserRolesOut)  # type: ignore

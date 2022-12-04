import datetime
from datetime import timedelta
from typing import Any, Union
from uuid import UUID


from sqlalchemy.orm import Session
from src.config import Settings, setup_logger
from src.exceptions import (
    BaseConflictException,
    BaseNotFoundException,
    GeneralException,
)
from src.pagination import OrderBy, OrderDirection
from src.service import (
    BaseService,
    ServiceResult,
    failed_service_result,
    success_service_result,
)

from src.users import schemas
from src.users.crud.roles import RoleCRUD
from src.users.crud.users import UserCRUD
from src.users.models import Roles, User, UserRoles


class RolesService(BaseService):
    def __init__(
        self, requesting_user: schemas.UserOut, db: Session, app_settings: Settings
    ) -> None:
        super().__init__(requesting_user, db)
        self.users_crud = UserCRUD(db)
        self.roles_crud = RoleCRUD(db)
        self.app_settings: Settings = app_settings
        self.logger = setup_logger()

        if requesting_user is None:
            raise GeneralException("Requesting User was not provided.")

    def create_role(
        self, role_data: schemas.RoleCreate
    ) -> ServiceResult[Union[Roles, None]]:
        created_by = self.users_crud.get_user_by_email(self.requesting_user.email)

        try:
            role_created = self.roles_crud.create_role(
                role_data.title,
                permissions=role_data.permissions,
                created_by=created_by,
            )
            return success_service_result(role_created)
        except BaseConflictException as raised_exception:
            return failed_service_result(raised_exception)

    def update_role(self, role_id: UUID, title: str = None, permissions: list[str] = None) -> ServiceResult[schemas.RoleOut]:  # type: ignore

        try:
            updated_role = self.roles_crud.update_role(
                role_id=role_id,
                updated_by=self.users_crud.get_user_by_email(
                    self.requesting_user.email
                ),
                title=title,
                permissions=permissions,
            )
            return success_service_result(updated_role)
        except BaseConflictException as raised_exception:
            return failed_service_result(raised_exception)

    def get_roles(
        self,
        start: int = 0,
        limit: int = 10,
        title: str = None,  # type: ignore
        order_by: OrderBy = OrderBy.DATE_CREATED,
        order_direction: OrderDirection = OrderDirection.ASC,
    ) -> ServiceResult[schemas.ManyRolesOut]:
        roles = self.roles_crud.get_roles(
            self.requesting_user.id,
            start=start,
            limit=limit,
            title=title,
            order_by=order_by,
            order_direction=order_direction,
        )
        total_roles = self.roles_crud.total_roles(title=title)
        data = schemas.ManyRolesOut.parse_obj({"total": total_roles, "roles": roles})

        return success_service_result(data)

    def get_role(self, role_id) -> ServiceResult[schemas.RoleOut]:
        role = self.roles_crud.get_role(role_id)

        if not role:
            return failed_service_result(BaseNotFoundException("Role does not exist."))

        role_dict = {
            **role.__dict__,
            "created_by_user": role.created_by_user,
            "modified_by_user": role.modified_by_user,
        }
        return success_service_result(schemas.RoleOut.parse_obj(role_dict))

    def assign_role(
        self, role_id: UUID, user_id: UUID
    ) -> ServiceResult[schemas.UserOut]:
        role = self.roles_crud.get_role(role_id)

        if not role:
            return failed_service_result(BaseNotFoundException("Role does not exist."))

        user = self.users_crud.get_user(user_id)
        if not user:
            return failed_service_result(
                BaseNotFoundException(
                    "The user you want to assign the role to does not exist."
                )
            )

        try:
            self.roles_crud.assign_role(user, role)
            user: User = self.users_crud.get_user(user.id)  # type: ignore
            return success_service_result(
                schemas.UserOut.parse_obj(
                    {**user.__dict__, "user_roles": user.user_roles}  # type: ignore
                )
            )
        except BaseConflictException as raised_exception:
            return failed_service_result(exception=raised_exception)

    def unassign_role(
        self, role_id: UUID, user_id: UUID
    ) -> ServiceResult[schemas.UserOut]:
        try:
            self.roles_crud.unassign_role(user_id, role_id)
            return success_service_result(self.users_crud.get_user(user_id))
        except BaseNotFoundException as raised_exception:
            return failed_service_result(raised_exception)

    def delete_role(self, role_id: UUID) -> ServiceResult[int]:
        try:
            total_users_role_removed_from = self.roles_crud.delete_role(role_id)
            return success_service_result(total_users_role_removed_from)
        except BaseNotFoundException as raised_exception:
            return failed_service_result(raised_exception)

    def get_users_assigned_to_role(
        self, role_id: UUID, skip: int = 0, limit: int = 10
    ) -> ServiceResult[schemas.ManyUserRolesOut]:
        users_roles = self.roles_crud.get_user_assigned_to_roles(role_id, skip, limit)
        total_user_roles = self.roles_crud.get_total_user_assigned_to_role(role_id)

        user_roles = schemas.ManyUserRolesOut.parse_obj(
            {"total": total_user_roles, "user_roles": users_roles}
        )

        return success_service_result(user_roles)

from typing import Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.config import setup_logger
from src.exceptions import BaseConflictException, BaseNotFoundException
from src.pagination import OrderBy, OrderDirection
from src.users import models


class RoleCRUD:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = setup_logger()

    def assign_role(self, user: models.User, role: models.Roles) -> models.UserRoles:
        try:
            db_user_role = models.UserRoles(user_id=user.id, role_id=role.id)
            self.db.add(db_user_role)

            self.db.commit()
            self.db.refresh(db_user_role)
            return db_user_role
        except IntegrityError as raised_exception:
            raise BaseConflictException(
                "You have already assign this role to this user."
            ) from raised_exception

    def unassign_role(self, user_id: UUID, role_id: UUID) -> None:
        db_user_role = (
            self.db.query(models.UserRoles)
            .filter(
                models.UserRoles.role_id == role_id,
                models.UserRoles.user_id == user_id,
            )
            .first()
        )
        if not db_user_role:
            raise BaseNotFoundException(
                "The system can not find the role for this user."
            )
        self.db.delete(db_user_role)
        self.db.commit()

    def delete_role(self, role_id: UUID) -> int:
        db_role = self.db.query(models.Roles).filter(models.Roles.id == role_id).first()
        if not db_role:
            raise BaseNotFoundException("The role does not exist.")

        # * deletes all the UserRole that has the role
        total_user_roles_to_deleted = (
            self.db.query(models.UserRoles)
            .filter(models.UserRoles.role_id == role_id)
            .delete()
        )
        self.db.delete(db_role)
        self.db.commit()

        return total_user_roles_to_deleted

    def create_role(
        self, title: str, permissions: list[str], created_by: models.User
    ) -> models.Roles:
        try:
            db_role = models.Roles(
                title=title.lower(), permissions=permissions, created_by=created_by.id
            )
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)
            return db_role
        except IntegrityError as raised_exception:
            raise BaseConflictException(
                "You have already created a role with that title, suggest a new title."
            ) from raised_exception

    def update_role(self, role_id: UUID, updated_by: models.User, title: str = None, permissions: list[str] = None) -> models.Roles:  # type: ignore
        try:
            db_role: models.Roles = self.db.query(models.Roles).filter(models.Roles.id == role_id).first()  # type: ignore

            if not db_role:
                raise BaseNotFoundException("The role does not exist")

            if title:
                setattr(db_role, "title", title.lower())

            if permissions:
                setattr(db_role, "permissions", permissions)

            db_role.modified_by = updated_by.id
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)

            return db_role
        except IntegrityError as raised_exception:
            raise BaseConflictException(
                "You have already created a role with that title, suggest a new title."
            ) from raised_exception

    def get_roles(
        self,
        user_id: UUID,
        start: int = 0,
        limit: int = 10,
        title: str = None,  # type: ignore
        order_by: OrderBy = OrderBy.DATE_CREATED,
        order_direction: OrderDirection = OrderDirection.ASC,
    ) -> list[models.Roles]:

        order_by_object = models.Roles.date_created
        if order_by == OrderBy.DATE_MODIFIED:
            order_by_object = models.Roles.date_created

        if order_direction == OrderDirection.ASC:
            order_by_object = order_by_object.asc()
        else:
            order_by_object = order_by_object.desc()

        query = self.db.query(models.Roles).order_by(order_by_object)

        if title:
            query = query.filter(models.Roles.title.contains(title.lower()))

        query = query.limit(limit).offset(start)
        query = query.all()

        return query

    def get_user_assigned_to_roles(
        self, role_id: UUID, skip: int = 0, limit: int = 10
    ) -> list[models.UserRoles]:
        all_users = (
            self.db.query(models.UserRoles)
            .filter(models.UserRoles.role_id == role_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return all_users

    def get_total_user_assigned_to_role(self, role_id: UUID) -> int:
        total_users_count = (
            self.db.query(models.UserRoles)
            .filter(models.UserRoles.role_id == role_id)
            .count()
        )

        return total_users_count

    def get_role(self, role_id: UUID) -> Union[None, models.Roles]:
        return self.db.query(models.Roles).filter(models.Roles.id == role_id).first()

    def total_roles(self, title: str = None) -> int:  # type: ignore
        query = self.db.query(models.Roles)
        if title:
            query = query.filter(models.Roles.title.contains(title.lower()))

        return query.count()

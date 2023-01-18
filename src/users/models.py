"""Contains the DB modules"""

import uuid
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Date,
    String,
    ARRAY,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql

from sqlalchemy.sql.functions import func

from src.database import Base
from src.models import FileObject
from src.scopes import ProfileScope, RoleScope, UserScope


class User(Base):
    __tablename__ = "users"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    is_super_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    access_begin = Column(DateTime)
    access_end = Column(DateTime, nullable=True)

    # user.items
    profile_id = Column(ForeignKey("profile.id"), index=True, nullable=True)
    profile = relationship("Profile", back_populates="user", lazy="joined")

    user_roles = relationship("UserRoles", back_populates="user")

    last_password_token = Column(String, default="")

    @staticmethod
    def full_scopes() -> list[str]:
        return [
            UserScope.CREATE.value,
            UserScope.READ.value,
            UserScope.UPDATE.value,
            UserScope.DELETE.value,
        ]


class UserRoles(Base):
    __tablename__ = "user_roles"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="user_roles")

    role_id = Column(postgresql.UUID(as_uuid=True), ForeignKey("roles.id"))
    role = relationship("Roles", foreign_keys=[role_id], lazy="joined")

    __table_args__ = (
        UniqueConstraint(
            user_id, role_id, name="user_id_and_role_id_unique_constraint"
        ),
    )


class Profile(Base):
    __tablename__ = "profile"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    avatar_url = Column(String, nullable=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    dob = Column(Date, nullable=True)

    user = relationship("User", back_populates="profile", lazy="joined")

    photo_file_id = Column(postgresql.UUID(as_uuid=True), ForeignKey("file_object.id"))
    photo_file = relationship(FileObject, foreign_keys=[photo_file_id], lazy="joined")

    @staticmethod
    def full_scopes() -> list[str]:
        return [
            ProfileScope.CREATE.value,
            ProfileScope.READ.value,
            ProfileScope.UPDATE.value,
            ProfileScope.DELETE.value,
        ]


class Roles(Base):

    __tablename__ = "roles"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    title = Column(String, index=True, unique=True)
    permissions = Column(ARRAY(String), default=[])
    can_be_deleted = Column(Boolean, default=True)

    # https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by = Column(ForeignKey("users.id"), index=True)

    modified_by = Column(ForeignKey("users.id"), nullable=True)

    # * constraints between title and created
    # __table_args__ = (UniqueConstraint(title, created_by, name="title_created_by"),)

    created_by_user = relationship("User", foreign_keys=[created_by], lazy="joined")
    modified_by_user = relationship("User", foreign_keys=[modified_by], lazy="joined")

    @staticmethod
    def full_scopes() -> list[str]:
        return [
            RoleScope.CREATE.value,
            RoleScope.READ.value,
            RoleScope.UPDATE.value,
            RoleScope.DELETE.value,
        ]

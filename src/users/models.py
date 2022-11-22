"""Contains the DB modules"""

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, Date, String, ARRAY, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql

from sqlalchemy.sql.functions import func

from src.database import Base
from src.users.permissions import get_regular_user_permissions


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

    # user.items
    profile_id = Column(ForeignKey("profile.id"), index=True, nullable=True)
    profile = relationship("Profile", back_populates="user")

    user_roles = relationship("UserRoles", back_populates="user")


class UserRoles(Base):
    __tablename__ = "user_roles"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="user_roles")

    role_id = Column(postgresql.UUID(as_uuid=True), ForeignKey("roles.id"))


class Profile(Base):
    __tablename__ = "profile"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    avatar_url = Column(String, nullable=True)
    other_names = Column(String(100))
    last_name = Column(String(100))
    dob = Column(Date, nullable=True)

    user = relationship("User", back_populates="profile")


class Roles(Base):

    __tablename__ = "roles"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    permissions = Column(ARRAY(String), default=[])
    can_be_deleted = Column(Boolean, default=True)

    # https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    created_by = Column(ForeignKey("users.id"), index=True)

    modified_by = Column(ForeignKey("users.id"), nullable=True)
    # modified_by = Column(UUID(as_uuid=True), nullable=True)

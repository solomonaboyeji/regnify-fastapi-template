"""Pydantic Models"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, constr, validator, EmailStr

from src.users.models import Profile, Roles, User


class AppBaseModel(BaseModel):
    class Config:
        orm_mode = True


class UserBase(AppBaseModel):
    email: EmailStr

    # Pre-processing validator that evaluates lazy relationships before any other validation
    # NOTE: If high throughput/performance is a concern, you can/should probably apply
    #       this validator in a more targeted fashion instead of a wildcard in a base class.
    #       This approach is by no means slow, but adds a minor amount of overhead for every field
    @validator("*", pre=True)
    def load_profile(cls, v):
        if isinstance(v, Profile):
            return ProfileOut.from_orm(v)
        return v


class UserCreate(UserBase):
    is_super_admin: bool = False
    last_name: constr(max_length=100)  # type: ignore
    first_name: constr(max_length=100)  # type: ignore
    password: str

    access_begin: Optional[datetime]
    access_end: Optional[datetime]


class UserUpdate(AppBaseModel):
    is_active: Optional[bool] = None
    is_super_admin: Optional[bool] = None
    last_name: Optional[constr(max_length=100)]  # type: ignore
    first_name: Optional[constr(max_length=100)]  # type: ignore


class ChangePassword(AppBaseModel):
    password: str


class ChangePasswordWithToken(AppBaseModel):
    token: str
    new_password: constr(max_length=255)  # type: ignore


class ProfileBase(AppBaseModel):
    last_name: constr(max_length=100)  # type: ignore
    first_name: constr(max_length=100)  # type: ignore
    avatar_url: str


class ProfileCreate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    pass
    # id: UUID


class MiniRoleOut(AppBaseModel):
    title: str
    permissions: list[str]


class MiniUserRoleOut(AppBaseModel):
    role: MiniRoleOut


class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_super_admin: bool
    user_roles: list[MiniUserRoleOut]
    profile: ProfileOut


class ManyUsersInDB(AppBaseModel):
    total: int = 0
    data: list[UserOut]


class RoleOut(AppBaseModel):
    id: UUID
    title: str
    permissions: list[str]
    can_be_deleted: bool
    created_by_user: UserOut
    modified_by_user: Optional[UserOut]
    date_created: datetime
    date_modified: Optional[datetime]


class UserRoleOut(AppBaseModel):
    role: RoleOut


class ManyUserRolesOut(AppBaseModel):
    total: int
    user_roles: list[UserRoleOut]


class RoleCreate(AppBaseModel):
    title: str
    permissions: list[str]


class ManyRolesOut(AppBaseModel):
    # @validator("*", pre=True)
    # def load_profile(cls, v):
    #     if isinstance(v, Roles):
    #         return RoleOut.from_orm(v)
    #     return v

    roles: list[RoleOut]
    total: int


class UserInDB(UserOut):
    hashed_password: str


class ItemBase(AppBaseModel):
    title: str
    description: Optional[str]


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: UUID
    owner_id: int


class ManyItems(AppBaseModel):
    total: int = 0
    data: list[Item]

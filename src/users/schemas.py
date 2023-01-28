"""Pydantic Models"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, constr, EmailStr
from src.schemas import ParentPydanticModel


class SystemScopeOut(BaseModel):
    title: str
    scopes: list[str]


class ManySystemScopeOut(BaseModel):
    scopes: list[SystemScopeOut]


class UserBase(ParentPydanticModel):
    email: EmailStr
    access_begin: Optional[datetime]
    access_end: Optional[datetime]


class UserCreate(UserBase):
    is_super_admin: bool = False
    last_name: constr(max_length=100)  # type: ignore
    first_name: constr(max_length=100)  # type: ignore
    password: str


class UserUpdate(ParentPydanticModel):
    is_active: Optional[bool] = None
    is_super_admin: Optional[bool] = None
    last_name: Optional[constr(max_length=100)] = None  # type: ignore
    first_name: Optional[constr(max_length=100)] = None  # type: ignore
    last_login: Optional[datetime] = None
    access_begin: Optional[datetime] = None
    access_end: Optional[datetime] = None


class ChangePassword(ParentPydanticModel):
    password: str


class ChangePasswordWithToken(ParentPydanticModel):
    token: str
    new_password: constr(max_length=255)  # type: ignore


class ProfileBase(ParentPydanticModel):
    last_name: constr(max_length=100)  # type: ignore
    first_name: constr(max_length=100)  # type: ignore
    avatar_url: str


class ProfileCreate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    pass
    # id: UUID


class MiniRoleOut(ParentPydanticModel):
    title: str
    permissions: list[str]


class MiniUserRoleOut(ParentPydanticModel):
    role: MiniRoleOut


class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_super_admin: bool
    user_roles: list[MiniUserRoleOut]
    profile: ProfileOut
    last_login: Optional[datetime]


class ManyUsersInDB(ParentPydanticModel):
    total: int = 0
    data: list[UserOut]


class RoleOut(ParentPydanticModel):
    id: UUID
    title: str
    permissions: list[str]
    can_be_deleted: bool
    created_by_user: UserOut
    modified_by_user: Optional[UserOut]
    date_created: datetime
    date_modified: Optional[datetime]


class UserRoleOut(ParentPydanticModel):
    role: RoleOut


class ManyUserRolesOut(ParentPydanticModel):
    total: int
    user_roles: list[UserRoleOut]


class RoleCreate(ParentPydanticModel):
    title: str
    permissions: list[str]


class ManyRolesOut(ParentPydanticModel):
    # @validator("*", pre=True)
    # def load_profile(cls, v):
    #     if isinstance(v, Roles):
    #         return RoleOut.from_orm(v)
    #     return v

    roles: list[RoleOut]
    total: int


class UserInDB(UserOut):
    hashed_password: str


class ItemBase(ParentPydanticModel):
    title: str
    description: Optional[str]


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: UUID
    owner_id: UUID


class ManyItems(ParentPydanticModel):
    total: int = 0
    data: list[Item]

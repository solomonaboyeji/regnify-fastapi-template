"""Pydantic Models"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, constr


class UserBase(BaseModel):
    email: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    is_super_admin: bool = False
    last_name: constr(max_length=100)  # type: ignore
    first_name: constr(max_length=100)  # type: ignore
    password: str


class MiniRoleOut(BaseModel):
    permissions: list[str]


class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_super_admin: bool
    user_roles: list[MiniRoleOut]


class ManyUsersInDB(BaseModel):
    total: int = 0
    data: list[UserOut]

    class Config:
        orm_mode = True


class RoleOut(BaseModel):
    permissions: list[str]
    can_be_deleted: bool
    created_by: UserOut
    modified_by: Optional[UserOut]
    date_created: datetime
    date_modified: datetime


class UserInDB(UserOut):
    hashed_password: str


class ItemBase(BaseModel):
    title: str
    description: Optional[str]


class ProfileBase(BaseModel):
    last_name: constr(max_length=100)  # type: ignore
    other_names: constr(max_length=100)  # type: ignore
    avatar_url: str


class ProfileCreate(ProfileBase):
    pass


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: UUID
    owner_id: int

    class Config:
        orm_mode = True


class ManyItems(BaseModel):
    total: int = 0
    data: list[Item]

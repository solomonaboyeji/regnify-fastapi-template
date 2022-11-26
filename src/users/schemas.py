"""Pydantic Models"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, constr, validator, EmailStr

from src.users.models import Profile


class UserBase(BaseModel):
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

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    is_super_admin: bool = False
    last_name: constr(max_length=100)  # type: ignore
    first_name: constr(max_length=100)  # type: ignore
    password: str


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_super_admin: Optional[bool] = None
    last_name: Optional[constr(max_length=100)]  # type: ignore
    first_name: Optional[constr(max_length=100)]  # type: ignore


class ChangePassword(BaseModel):
    password: str


class ChangePasswordWithToken(BaseModel):
    token: str
    new_password: constr(max_length=255)  # type: ignore


class MiniRoleOut(BaseModel):
    permissions: list[str]


class ProfileBase(BaseModel):
    last_name: constr(max_length=100)  # type: ignore
    first_name: constr(max_length=100)  # type: ignore
    avatar_url: str

    class Config:
        orm_mode = True


class ProfileCreate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    pass
    # id: UUID


class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_super_admin: bool
    user_roles: list[MiniRoleOut]
    profile: ProfileOut

    class Config:
        orm_mode = True


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

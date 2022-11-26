from typing import List
from uuid import UUID
from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: UUID
    email: str
    is_super_admin: bool
    scopes: List[str] = []

from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: str

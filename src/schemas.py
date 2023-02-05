from pydantic import BaseModel


class ParentPydanticModel(BaseModel):
    class Config:
        orm_mode = True

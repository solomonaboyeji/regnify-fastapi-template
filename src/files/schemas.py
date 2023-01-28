from typing import List
from uuid import UUID

from src.schemas import ParentPydanticModel


class BucketOut(ParentPydanticModel):
    name: str


class FileObjectOut(ParentPydanticModel):
    id: UUID
    file_name: str
    original_file_name: str
    bucket: BucketOut


class ManyFileObjectsOut(ParentPydanticModel):
    total: int
    total_bytes: int
    file_objects: List[FileObjectOut]

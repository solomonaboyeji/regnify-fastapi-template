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
    mime_type: str
    extension: str


class MiniFileObjectOut(ParentPydanticModel):
    id: UUID
    original_file_name: str


class ManyFileObjectsOut(ParentPydanticModel):
    total: int
    total_bytes: int
    file_objects: List[FileObjectOut]

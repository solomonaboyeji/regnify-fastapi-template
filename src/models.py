from email.policy import default
import uuid
from sqlalchemy import Column, ForeignKey, Date, String, DateTime, Integer

from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import relationship

from src.database import Base


class Bucket(Base):
    __tablename__ = "bucket"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name = Column(String(63))

    owner_id = Column(postgresql.UUID(as_uuid=True), ForeignKey("users.id"))

    date_created = Column(DateTime(timezone=True), server_default=func.now())


class FileObject(Base):
    __tablename__ = "file_object"

    id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    file_name = Column(String(255))
    original_file_name = Column(String(255))

    backend_storage = Column(String(255), default="NOT_SPECIFIED")

    total_bytes = Column(Integer, default=0)

    bucket_id = Column(postgresql.UUID(as_uuid=True), ForeignKey("bucket.id"))
    bucket = relationship(Bucket, foreign_keys=[bucket_id], lazy="joined")

    date_created = Column(DateTime(timezone=True), server_default=func.now())

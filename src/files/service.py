from sqlalchemy.orm import Session

from io import BufferedReader, BytesIO
from uuid import UUID
from filetype import filetype

from src.models import Bucket, FileObject

from src.files.storage import BackendStorage
from src.files.utils import S3FileData, format_bucket_name, make_custom_id
from src.service import BaseService
from src.users import schemas
from src.config import Settings, setup_logger
from src.exceptions import (
    GeneralException,
    BaseNotFoundException,
    BaseConflictException,
)
from src.files.crud import FileCRUD


class FileService(BaseService):
    def __init__(
        self, requesting_user: schemas.UserOut, db: Session, app_settings: Settings
    ) -> None:
        super().__init__(requesting_user, db)
        self.crud = FileCRUD(db)
        self.app_settings: Settings = app_settings
        self.logger = setup_logger()
        self.backend_storage = BackendStorage(self.app_settings)

        if requesting_user is None:
            raise GeneralException("Requesting User was not provided.")

    def _ensure_s3_bucket_exists(self, owner_id: UUID):
        bucket_name = format_bucket_name(owner_id)
        if not self.backend_storage.bucket_exists(bucket_name):
            if self.crud.get_owner_bucket(owner_id) is None:
                self.crud.create_bucket(owner_id)
            else:
                self.crud.get_owner_bucket(owner_id)

            self.backend_storage.create_bucket(bucket_name)

    def get_bucket_by_name(self, bucket_name: str) -> Bucket:
        db_bucket = self.db.query(Bucket).filter(Bucket.name == bucket_name).first()

        if not db_bucket:
            raise BaseNotFoundException("The bucket does not exist.")

        return db_bucket

    def get_bucket_by_id(self, bucket_id: str):
        db_bucket = self.db.query(Bucket).filter(Bucket.id == bucket_id).first()

        if not db_bucket:
            raise BaseNotFoundException("The bucket does not exist.")

        return db_bucket

    def init_buckets_for_user(self, user_id: UUID):
        """Ensures the database bucket and the s3 bucket for this user exists."""

        try:
            db_bucket = self.crud.create_bucket(user_id)
        except BaseConflictException:
            db_bucket = self.crud.get_owner_bucket(user_id)

        try:
            self._ensure_s3_bucket_exists(user_id)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            raise GeneralException(
                "The API is unable to create an S3 Bucket for this user."
            )

        return db_bucket

    def upload_file(self, buffer: BufferedReader, user_id: UUID, file_name: str):
        try:
            extension = filetype.guess_extension(buffer)
        except TypeError:
            raise GeneralException(
                "Unable to determine extension of file. Ensure the uploaded file is a file-object."
            )

        file_name_split = file_name.split(f".{extension}")
        if len(file_name_split) > 0:
            original_file_name_without_extension = file_name_split[0]
        else:
            raise GeneralException(
                "Unable to pick the name of this file, ensure the file has extension, i.e. <file-name>.<extension>."
            )

        new_file_name = (
            f"{original_file_name_without_extension}-{make_custom_id()}.{extension}"
        )

        self.init_buckets_for_user(user_id)

        s3_file_data = S3FileData(
            file_name=new_file_name,
            bucket_name=format_bucket_name(user_id),
            original_file_name=file_name,
        )

        try:
            total_bytes = self.backend_storage.upload_file(
                buffer=buffer, s3_file_data=s3_file_data
            )
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            raise GeneralException("There was a problem uploading the file")

        return self.crud.save_file(
            file_name=new_file_name,
            original_file_name=file_name,
            owner_id=user_id,
            total_bytes=total_bytes,
        )

    def download_file(self, file_object: FileObject) -> BytesIO:
        s3_file_data = S3FileData(
            file_name=str(file_object.file_name),
            original_file_name=str(file_object.original_file_name),
            bucket_name=file_object.bucket.name,
        )
        return self.backend_storage.download_file(s3_file_data)

    def get_signed_upload_url(self, owner_id: UUID, file_name: str):
        return self.backend_storage.get_signed_upload_url(
            format_bucket_name(owner_id), file_name
        )

    def get_signed_download_url(self, owner_id: UUID, file_name: str):
        self._ensure_s3_bucket_exists(owner_id)
        return self.backend_storage.get_signed_download_url(
            format_bucket_name(owner_id), file_name
        )

    def validate_file(self, owner_id: UUID, file_name: str):

        # * TODO: ensure file name has extension

        # *  TODO: ensure file fits supported extensions

        # * TODO:  ensure file fits file limit

        pass

    def delete_file(self, owner_id: UUID, file_name: str):
        self.backend_storage.remove_file(format_bucket_name(owner_id), file_name)

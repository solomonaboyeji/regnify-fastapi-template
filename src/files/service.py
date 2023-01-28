from typing import Union
from uuid import UUID
from sqlalchemy.orm import Session

from io import BufferedReader, BytesIO
from filetype import filetype
from src.files.schemas import FileObjectOut, ManyFileObjectsOut
from src.service import ServiceResult, success_service_result, failed_service_result

from src.models import Bucket, FileObject
from src.exceptions import FILE_DOES_NOT_EXIST_ERROR_MESSAGE, FileTooLargeException

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

    def _ensure_s3_bucket_exists(self, owner_id):
        bucket_name = format_bucket_name(owner_id)
        if not self.backend_storage.bucket_exists(bucket_name):
            if self.crud.get_owner_bucket(owner_id) is None:
                self.crud.create_bucket(owner_id)
            else:
                self.crud.get_owner_bucket(owner_id)

            self.backend_storage.create_bucket(bucket_name)

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

    def upload_file(
        self, buffer: BufferedReader, user_id: UUID, file_name: str
    ) -> ServiceResult[Union[FileObjectOut, GeneralException]]:
        try:
            extension = filetype.guess_extension(buffer)
        except TypeError:
            return failed_service_result(
                GeneralException(
                    "Unable to determine extension of file. Ensure the uploaded file is a file-object."
                )
            )

        file_name_split = file_name.split(f".{extension}")
        if len(file_name_split) > 0:
            original_file_name_without_extension = file_name_split[0]
        else:
            return failed_service_result(
                GeneralException(
                    "Unable to pick the name of this file, ensure the file has extension, i.e. <file-name>.<extension>."
                )
            )

        new_file_name = (
            f"{original_file_name_without_extension}-{make_custom_id()}.{extension}"
        )

        try:
            self.init_buckets_for_user(user_id)
        except GeneralException as raised_exception:
            return failed_service_result(raised_exception)

        s3_file_data = S3FileData(
            file_name=new_file_name,
            bucket_name=format_bucket_name(user_id),
            original_file_name=file_name,
        )

        try:
            total_bytes = self.backend_storage.upload_file(
                buffer=buffer, s3_file_data=s3_file_data
            )
        except FileTooLargeException as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

        try:

            file_object = self.crud.save_file(
                file_name=new_file_name,
                original_file_name=file_name,
                owner_id=user_id,
                total_bytes=total_bytes,
            )
            return success_service_result(FileObjectOut.parse_obj(file_object.__dict__))
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(
                GeneralException("There was a problem uploading the file.")
            )

    def download_file(
        self, file_object_id: UUID
    ) -> ServiceResult[Union[BytesIO, GeneralException, BaseNotFoundException]]:
        file_object_result = self.get_file(file_object_id=file_object_id)
        if not file_object_result.success:
            return failed_service_result(file_object_result.exception)

        file_object_data: FileObject = file_object_result.data
        s3_file_data = S3FileData(
            file_name=str(file_object_data.file_name),
            original_file_name=str(file_object_data.original_file_name),
            bucket_name=file_object_data.bucket.name,
        )
        try:
            return success_service_result(
                self.backend_storage.download_file(s3_file_data)
            )
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(
                GeneralException("There was a problem downloading the file.")
            )

    def delete_file(
        self, owner_id, file_object_id: UUID
    ) -> ServiceResult[Union[None, BaseNotFoundException, GeneralException]]:

        file_object = self.crud.get_file(file_object_id)
        if not file_object:
            return failed_service_result(
                BaseNotFoundException(FILE_DOES_NOT_EXIST_ERROR_MESSAGE)
            )

        try:
            self.backend_storage.remove_file(
                format_bucket_name(owner_id), str(file_object.file_name)
            )
            self.crud.remove_file(file_object_id)
            return success_service_result(None)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(
                GeneralException("There was a problem removing the file.")
            )

    def get_file(
        self, file_object_id: UUID
    ) -> ServiceResult[Union[FileObjectOut, BaseNotFoundException]]:
        file_object = self.crud.get_file(file_object_id)

        if file_object is None:
            return failed_service_result(
                BaseNotFoundException(FILE_DOES_NOT_EXIST_ERROR_MESSAGE)
            )

        return success_service_result(FileObjectOut.parse_obj(file_object.__dict__))

    def get_files(
        self, user_id: UUID, skip: int = 0, limit: int = 10
    ) -> ServiceResult[ManyFileObjectsOut]:
        file_objects = self.crud.get_files(owner_id=user_id, skip=skip, limit=limit)
        total_bytes = self.crud.get_total_bytes_used(owner_id=user_id)
        total_files = self.crud.total_files(owner_id=user_id)

        result = {
            "total_bytes": total_bytes,
            "file_objects": file_objects,
            "total": total_files,
        }

        return success_service_result(ManyFileObjectsOut.parse_obj(result))

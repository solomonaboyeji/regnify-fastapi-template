from datetime import timedelta
from fileinput import filename
from io import BytesIO
import mimetypes
import os
from minio import Minio

from minio.error import MinioException

from src.files.clients.client import BaseS3Client
from src.exceptions import GeneralException


class MinioClient(BaseS3Client):
    def __init__(self) -> None:
        self.client = Minio(
            self.settings.minio_host,
            access_key=self.settings.minio_access_key,
            secret_key=self.settings.minio_secret_key,
            secure=self.settings.secure_minio,
        )

    def print_handled_message(self, err: MinioException):
        self.logger.info("MINIO Exception: Handled Gracefully")
        self.logger.exception(err)

    def make_bucket(self, name: str):
        try:
            self.client.make_bucket(name)
        except MinioException as err:
            self.print_handled_message(err)
            raise GeneralException("Unable to create S3 bucket.")

    def bucket_exists(self, name: str) -> bool:
        try:
            return self.client.bucket_exists(name)
        except MinioException as err:
            self.print_handled_message(err)

        return False

    def stream_upload(self, buffer: BytesIO, bucket_name: str, file_name: str):
        if buffer.seekable():
            buffer.seek(0)

        from filetype import filetype
        from src.files.utils import make_custom_id

        try:
            mime_type = filetype.guess_mime(buffer)
            if mime_type is None:
                raise TypeError()
        except TypeError:
            self.logger.error(
                "Unable to detect the mime type of this file, resetting it to application/octet-stream"
            )
            mime_type = "application/octet-stream"

        try:
            extension = filetype.guess_extension(buffer)
        except TypeError:
            raise GeneralException(
                "Unable to determine extension of file. Ensure the uploaded file is a file-object."
            )

        original_file_name_without_extension = file_name.split("/")[-1]
        size = os.fstat(buffer.fileno()).st_size
        new_file_name = (
            f"{original_file_name_without_extension}-{make_custom_id()}.{extension}"
        )

        bytes_per_stream = size
        if size > self.settings.upload_file_bytes_per_stream:
            bytes_per_stream = self.settings.upload_file_bytes_per_stream

        result = self.client.put_object(
            bucket_name=bucket_name,
            object_name=new_file_name,
            data=buffer,
            length=bytes_per_stream,
            content_type=mime_type,
        )

        print(
            "created {0} object; etag: {1}, version-id: {2}".format(
                result.object_name,
                result.etag,
                result.version_id,
            )
        )

    def remove_file_object(self, bucket_name: str, file_name: str):
        try:
            self.client.remove_object(bucket_name, file_name)
        except MinioException as err:
            self.print_handled_message(err)
            raise GeneralException("Unable to remove S3 bucket.")

    def presigned_download_url(self, bucket_name: str, file_name: str) -> str:
        try:
            return self.client.presigned_get_object(bucket_name, file_name)
        except MinioException as err:
            self.print_handled_message(err)
            raise GeneralException("Unable to generate a download URL")

    def presigned_upload_url(
        self, bucket_name: str, file_name: str, days_expiring: int
    ) -> str:
        try:
            return self.client.presigned_put_object(
                bucket_name, file_name, expires=timedelta(days=days_expiring)
            )
        except MinioException as err:
            self.print_handled_message(err)
            raise GeneralException("Unable to generate an upload URL")

    def get_file_size(self, bucket_name: str, file_name: str) -> str:
        try:
            file_object = self.client.stat_object(bucket_name, file_name)
            return str(file_object.size)
        except MinioException as err:
            self.print_handled_message(err)
            raise GeneralException("Unable to get file size.")

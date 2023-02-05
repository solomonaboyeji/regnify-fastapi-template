from urllib3.response import HTTPResponse
import os
from datetime import timedelta
from io import BufferedReader, BytesIO

from minio.helpers import ObjectWriteResult

from filetype import filetype
from minio import Minio

from minio.error import MinioException

from src.files.clients.client import BaseS3Client
from src.exceptions import GeneralException, FileTooLargeException
from src.config import Settings
from src.service import ONE_MB_IN_BYTES


class MinioClient(BaseS3Client):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)

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

    def download_file(self, bucket_name: str, file_name: str) -> BytesIO:
        try:
            response: HTTPResponse = self.client.get_object(bucket_name, file_name)
            return BytesIO(response.data)
        finally:
            response.close()  # type: ignore
            response.release_conn()  # type: ignore

    def upload_file(
        self,
        buffer: BytesIO,
        bucket_name: str,
        s3_file_name: str,
        mime_type: str,
        file_size_limit: int = -1,
    ):
        """
        Uploads the file to the correct S3 storage.

        Args:
            buffer (BufferedReader): The bytes of the file to upload.
            bucket_name (str): The name of the bucket to upload to.
            s3_file_name (str): The S3 compliance file name.
            file_size_limit (int): The file size limit (in bytes) to check the file's size against.

        Raises:
            TypeError: If the method is unable to determine the mime type of the file.
            FileTooLargeException: If the file is larger than the specified limit.

        Returns:
            int: The size of the uploaded file.

        """

        print(buffer.tell())
        print(len(buffer.read()))

        if buffer.seekable():
            buffer.seek(0)

        size = os.fstat(buffer.fileno()).st_size

        bytes_per_stream = size
        if size > self.settings.upload_file_bytes_per_stream:
            bytes_per_stream = self.settings.upload_file_bytes_per_stream

        expected_max_file_size = (
            self.settings.max_size_of_a_file
            if file_size_limit <= 0
            else file_size_limit
        )
        if size > expected_max_file_size:
            buffer.close()
            raise FileTooLargeException(
                f"The file being uploaded has a file size larger than the limit. Max allowed file size: { expected_max_file_size/  ONE_MB_IN_BYTES } mb"
            )

        _: ObjectWriteResult = self.client.put_object(
            bucket_name=bucket_name,
            object_name=s3_file_name,
            data=buffer,
            length=bytes_per_stream,
            content_type=mime_type,
        )

        return size

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
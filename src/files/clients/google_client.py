import datetime
from src.files.clients.client import BaseS3Client

import os
from typing import BinaryIO
from src.files.utils import seek_to_start, meet_upload_file_limit_rule
from google.cloud import storage
from google.cloud.exceptions import NotFound, Conflict

from src.files.clients.client import BaseS3Client
from src.exceptions import GeneralException, FileTooLargeException
from src.config import Settings


class GoogleS3Storage(BaseS3Client):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)

        self.client = storage.Client()

    def print_handled_message(self, err: Exception):
        self.logger.info("Google Storage Exception: Handled Gracefully")
        self.logger.exception(err)

    def _get_base_bucket(self):
        try:
            bucket = self.client.create_bucket(
                self.settings.base_gcs_bucket_name,
                location=self.settings.s3_bucket_location,
            )
        except Conflict:
            bucket = self.client.bucket(self.settings.base_gcs_bucket_name)

        return bucket

    def make_bucket(self, name: str):
        try:
            bucket = self._get_base_bucket()
            blob = bucket.blob("/" + name)
            blob.upload_from_string(
                "", content_type="application/x-www-form-urlencoded;charset=UTF-8"
            )
        except Exception as err:
            self.print_handled_message(err)
            raise GeneralException(
                "There was a problem creating this a storage bucket for this user."
            )

    def bucket_exists(self, name: str) -> bool:
        try:
            self.client.get_bucket(name)
            return True
        except NotFound as err:
            self.print_handled_message(err)
            return False

    def download_file(self, bucket_name: str, file_name: str) -> None:
        """
        Downloads the object to a file name, i.e. /tmp/{file_name}

        Args:
            bucket_name (str): The bucket to get this object from.
            file_name (str): The file name of the object.

        Raises:
            GeneralException: If there is a problem while downloading the object.
        """
        try:
            bucket = self._get_base_bucket()
            blob = bucket.blob(f"{bucket_name}/{file_name}")
            blob.download_to_filename(f"/tmp/{file_name}")
        except Exception as err:
            self.print_handled_message(err)
            raise GeneralException("There was a problem downloading this file.")

    def upload_file(
        self,
        file_to_upload: BinaryIO,
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

        seek_to_start(file_to_upload)  # type: ignore
        size = os.fstat(file_to_upload.fileno()).st_size

        try:
            self.logger.info(f"Using {file_size_limit} bytes as file limit")
            expected_max_file_size = (
                self.settings.max_size_of_a_file
                if file_size_limit <= 0
                else file_size_limit
            )
            meet_upload_file_limit_rule(
                file_to_upload, file_limit=expected_max_file_size
            )
        except GeneralException as raised_exception:
            raise FileTooLargeException(str(raised_exception))

        seek_to_start(file_to_upload)

        bucket = self._get_base_bucket()
        blob = bucket.blob(f"{bucket_name}/{s3_file_name}")
        blob.upload_from_file(file_to_upload, content_type=mime_type)

        return size

    def remove_file_object(self, bucket_name: str, file_name: str):
        try:
            bucket = self._get_base_bucket()
            bucket.delete_blob(f"{bucket_name}/{file_name}")
        except NotFound as err:
            self.print_handled_message(err)
            raise GeneralException("The file has been deleted from the final storage.")

    def presigned_download_url(self, bucket_name: str, file_name: str) -> str:
        try:
            bucket = self._get_base_bucket()
            blob = bucket.blob(f"{bucket_name}/{file_name}")
            url = blob.generate_signed_url(
                version="v4",
                # This URL is valid for
                expiration=datetime.timedelta(days=7),
                # Allow GET requests using this URL.
                method="GET",
            )
            return url
        except Exception as err:
            self.print_handled_message(err)
            raise GeneralException("Unable to generate a download URL")

    def presigned_upload_url(
        self, bucket_name: str, file_name: str, days_expiring: int
    ) -> str:
        try:
            bucket = self._get_base_bucket()
            blob = bucket.blob(f"{bucket_name}/{file_name}")
            url = blob.generate_signed_url(
                version="v4",
                # This URL is valid for
                expiration=datetime.timedelta(days=days_expiring),
                # Allow GET requests using this URL.
                method="PUT",
            )
            return url
        except Exception as err:
            self.print_handled_message(err)
            raise GeneralException("Unable to generate an upload URL")

    def get_file_size(self, bucket_name: str, file_name: str) -> str:
        self.logger.info("Google Cloud Storage does not return the file size.")
        return "0"

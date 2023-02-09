from genericpath import isfile
import os
from typing import BinaryIO
from src.config import Settings
from src.files.clients.google_client import GoogleS3Storage
from src.files.clients.minio_client import MinioClient
from src.files.utils import BackendStorageOption, S3FileData
from src.config import setup_logger
from src.exceptions import GeneralException


class BackendStorage:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = setup_logger()
        if settings.backend_storage_option == BackendStorageOption.MINIO_STORAGE.value:
            self.client = MinioClient(settings)
        elif (
            settings.backend_storage_option == BackendStorageOption.GOOGLE_STORAGE.value
        ):
            self._setup_google_application_credentials()
            self.client = GoogleS3Storage(settings)

    def _setup_google_application_credentials(self):
        google_application_credentials = self.settings.google_application_credentials
        google_application_credentials_json_content = (
            self.settings.google_application_credentials_json_content
        )
        if google_application_credentials is None:
            self.logger.debug(
                "GOOGLE_APPLICATION_CREDENTIALS is not provided, will be read from a privileged service account."
            )
        else:
            if google_application_credentials_json_content is None:
                self.logger.error(
                    "The GOOGLE_APPLICATION_CREDENTIALS_JSON_CONTENT needs to be provided."
                )
                raise GeneralException(
                    "The GOOGLE_APPLICATION_CREDENTIALS_JSON_CONTENT needs to be provided."
                )
            if os.path.isfile(google_application_credentials):
                os.remove(path=google_application_credentials)

            with open(google_application_credentials, "w") as f:
                f.write(google_application_credentials_json_content)

    def create_bucket(self, bucket_name: str):
        self.client.make_bucket(bucket_name)

    def bucket_exists(self, bucket_name: str):
        return self.client.bucket_exists(bucket_name)

    def upload_file(
        self,
        file_to_upload: BinaryIO,
        s3_file_data: S3FileData,
        mime_type: str,
        file_size_limit: int = -1,
    ) -> int:

        file_size = self.client.upload_file(
            file_to_upload=file_to_upload,
            bucket_name=s3_file_data.bucket_name,
            s3_file_name=s3_file_data.file_name,
            file_size_limit=file_size_limit,
            mime_type=mime_type,
        )
        return file_size

    def download_file(self, s3_file_data: S3FileData):
        return self.client.download_file(
            bucket_name=s3_file_data.bucket_name, file_name=s3_file_data.file_name
        )

    def get_signed_upload_url(self, bucket_name: str, file_name: str):
        return self.client.presigned_upload_url(bucket_name, file_name, days_expiring=7)

    def get_signed_download_url(self, bucket_name: str, file_name: str):
        return self.client.presigned_download_url(bucket_name, file_name)

    def remove_file(self, bucket_name: str, file_name: str):
        self.client.remove_file_object(bucket_name, file_name)

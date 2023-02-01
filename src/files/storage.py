from io import BufferedReader, BytesIO
from typing import Union
from src.config import Settings
from src.files.clients.minio_client import MinioClient
from src.files.utils import BackendStorageOption, S3FileData


class BackendStorage:
    def __init__(self, settings: Settings) -> None:
        if settings.backend_storage_option == BackendStorageOption.MINIO_STORAGE.value:
            self.client = MinioClient(settings)
        elif (
            settings.backend_storage_option == BackendStorageOption.GOOGLE_STORAGE.value
        ):
            raise NotImplementedError("Google Cloud Storage is not yet implemented.")

    def create_bucket(self, bucket_name: str):
        self.client.make_bucket(bucket_name)

    def bucket_exists(self, bucket_name: str):
        return self.client.bucket_exists(bucket_name)

    def upload_file(
        self,
        buffer: BytesIO,
        s3_file_data: S3FileData,
        mime_type: str,
        file_size_limit: int = -1,
    ) -> int:

        file_size = self.client.upload_file(
            buffer=buffer,
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

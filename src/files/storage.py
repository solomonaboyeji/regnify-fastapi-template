import enum
from src.config import Settings
from src.files.clients.client import BaseS3Client
from src.files.clients.minio_client import MinioClient


class BackendStorageOption(enum.Enum):
    MINIO_STORAGE: str = "MINIO_STORAGE"  # type: ignore
    GOOGLE_STORAGE: str = "GOOGLE_STORAGE"  # type: ignore


class BackendStorage:
    def __init__(self, settings: Settings) -> None:
        if settings.backend_storage_option == BackendStorageOption.MINIO_STORAGE.value:
            self.client = MinioClient()
        elif (
            settings.backend_storage_option == BackendStorageOption.GOOGLE_STORAGE.value
        ):
            raise NotImplementedError

    def create_bucket(self, bucket_name: str):
        self.client.make_bucket(bucket_name)

    def bucket_exists(self, bucket_name: str):
        return self.client.bucket_exists(bucket_name)

    def get_signed_upload_url(self, bucket_name: str, file_name: str):
        return self.client.presigned_upload_url(bucket_name, file_name, days_expiring=7)

    def get_signed_download_url(self, bucket_name: str, file_name: str):
        return self.client.presigned_download_url(bucket_name, file_name)

    def remove_file(self, bucket_name: str, file_name: str):
        self.client.remove_file_object(bucket_name, file_name)

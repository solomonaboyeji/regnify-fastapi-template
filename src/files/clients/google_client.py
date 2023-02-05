from minio.error import MinioException

from src.files.clients.client import BaseS3Client


class GoogleS3Storage(BaseS3Client):
    def __init__(self) -> None:
        self.client = None

    def print_handled_message(self, err: MinioException):
        self.logger.info("Google Storage Exception: Handled Gracefully")
        self.logger.exception(err)

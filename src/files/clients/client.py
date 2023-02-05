from src.config import Settings, setup_logger


class BaseS3Client:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = setup_logger()

    def make_bucket(self):
        raise NotImplementedError

    def bucket_exists(self):
        raise NotImplementedError

    def get_bucket(self):
        raise NotImplementedError

    def get_buckets(self):
        raise NotImplementedError

    def presigned_download_url(self):
        raise NotImplementedError

    def presigned_upload_url(self):
        raise NotImplementedError

    def get_file_info(self):
        raise NotImplementedError

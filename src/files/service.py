from uuid import UUID
from src.files.storage import BackendStorage
from src.service import BaseService
from src.users import schemas
from src.config import Settings, setup_logger
from sqlalchemy.orm import Session
from src.exceptions import GeneralException

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
        bucket_name = str(owner_id).replace("-", "")
        if not self.backend_storage.bucket_exists(bucket_name):
            if self.crud.get_bucket(owner_id) is None:
                self.crud.create_bucket(owner_id)
            else:
                self.crud.get_bucket(owner_id)

            self.backend_storage.create_bucket(bucket_name)

    def _parse_bucket_name(self, owner_id: UUID):
        return str(owner_id).replace("-", "")

    def get_signed_upload_url(self, owner_id: UUID, file_name: str):
        self._ensure_s3_bucket_exists(owner_id)
        return self.backend_storage.get_signed_upload_url(
            self._parse_bucket_name(owner_id), file_name
        )

    def get_signed_download_url(self, owner_id: UUID, file_name: str):
        self._ensure_s3_bucket_exists(owner_id)
        return self.backend_storage.get_signed_download_url(
            self._parse_bucket_name(owner_id), file_name
        )

    def validate_file(self, owner_id: UUID, file_name: str):

        # * TODO: ensure file name has extension

        # *  TODO: ensure file fits supported extensions

        # * TODO:  ensure file fits file limit

        pass

    def delete_file(self, owner_id: UUID, file_name: str):
        self.backend_storage.remove_file(self._parse_bucket_name(owner_id), file_name)

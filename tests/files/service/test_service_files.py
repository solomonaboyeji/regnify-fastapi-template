from src.files.utils import hash_bytes, hash_file
from src.files.service import FileService
from src.config import Settings
from tests.utils import FILE_FIXTURES_PATH


def test_upload_and_download_of_file(test_db, file_user):
    file_service = FileService(
        requesting_user=file_user, db=test_db, app_settings=Settings()
    )
    with open(f"{FILE_FIXTURES_PATH}/flower.jpg", "rb") as f:
        file_object = file_service.upload_file(
            buffer=f,
            user_id=file_user.id,
            file_name="simple-file.jpg",
        )

    file_content = file_service.download_file(file_object)

    assert hash_bytes(file_content.read()) == hash_file(
        f"{FILE_FIXTURES_PATH}/flower.jpg"
    )


def test_get_files():
    pass


def test_get_file():
    pass


def test_delete_file():
    pass

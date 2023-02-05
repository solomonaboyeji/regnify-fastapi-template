import os
from io import BytesIO
from uuid import uuid4
from src.files.utils import hash_bytes, hash_file
from src.files.service import FileService
from src.config import Settings
from tests.utils import FILE_FIXTURES_PATH
from src.service import ServiceResult
from src.exceptions import FileTooLargeException
from src.files.utils import ONE_MEGA_BYTE

from src.files.schemas import FileObjectOut, ManyFileObjectsOut

MAX_UPLOAD_COUNT = 5
FILE_PATH_UNDER_TEST = f"{FILE_FIXTURES_PATH}/flower.jpg"


def test_upload_and_download_of_file(test_db, file_user):
    file_service = FileService(
        requesting_user=file_user, db=test_db, app_settings=Settings()
    )

    user_files = file_service.get_files(file_user.id)
    assert isinstance(user_files, ServiceResult)
    assert isinstance(user_files.data, ManyFileObjectsOut)
    assert user_files.data.total_bytes == 0
    assert user_files.data.file_objects == []

    for _ in range(0, MAX_UPLOAD_COUNT):
        with open(FILE_PATH_UNDER_TEST, "rb") as f:
            file_object = file_service.upload_file(
                file_to_upload=f,
                user_id=file_user.id,
                file_name="simple-file.jpg",
            )
            assert isinstance(file_object, ServiceResult)
            assert file_object.success
            assert isinstance(file_object.data, FileObjectOut)

        file_object = file_service.get_file(file_object.data.id)
        assert isinstance(file_object.data, FileObjectOut)

        file_content = file_service.download_file(file_object.data.id)
        assert isinstance(file_content, ServiceResult)
        assert isinstance(file_content.data, BytesIO)

        assert hash_bytes(file_content.data.read()) == hash_file(
            f"{FILE_FIXTURES_PATH}/flower.jpg"
        )

    # * test get files
    with open(FILE_PATH_UNDER_TEST, "rb") as f:
        test_file_size_in_bytes = os.fstat(f.fileno()).st_size

    file_service = FileService(
        requesting_user=file_user, db=test_db, app_settings=Settings()
    )

    user_files = file_service.get_files(file_user.id)
    assert isinstance(user_files, ServiceResult)
    assert isinstance(user_files.data, ManyFileObjectsOut)
    assert user_files.data.total_bytes >= (test_file_size_in_bytes * MAX_UPLOAD_COUNT)
    assert len(user_files.data.file_objects) >= MAX_UPLOAD_COUNT
    assert user_files.data.total >= MAX_UPLOAD_COUNT


def test_get_file(test_db, file_user):
    file_service = FileService(
        requesting_user=file_user, db=test_db, app_settings=Settings()
    )

    user_files = file_service.get_files(file_user.id)
    assert isinstance(user_files.data, ManyFileObjectsOut)
    user_files = user_files.data
    the_file = user_files.file_objects[0]

    result = file_service.get_file(file_object_id=the_file.id)
    assert isinstance(result, ServiceResult)
    assert result.success
    assert isinstance(result.data, FileObjectOut)
    assert result.data.id == the_file.id

    # * what happens when a file does not exist
    result = file_service.get_file(file_object_id=uuid4())
    assert isinstance(result, ServiceResult)
    assert not result.success


def test_delete_file(test_db, file_user):
    file_service = FileService(
        requesting_user=file_user, db=test_db, app_settings=Settings()
    )

    user_files = file_service.get_files(file_user.id)
    assert isinstance(user_files.data, ManyFileObjectsOut)
    user_files = user_files.data
    the_file = user_files.file_objects[0]

    file_service.delete_file(file_user.id, file_object_id=the_file.id)

    result = file_service.get_file(file_object_id=the_file.id)
    assert not result.success


def test_upload_file_larger_than_limit(test_db, file_user):
    with open(FILE_PATH_UNDER_TEST, "rb") as f:
        test_file_size_in_bytes = os.fstat(f.fileno()).st_size

    assert test_file_size_in_bytes > 100  # 100bytes
    os.environ["MAX_SIZE_OF_A_FILE"] = "0.0001"  # mb (0.0001mb) == kb (100bytes)

    print(os.environ["MAX_SIZE_OF_A_FILE"], test_file_size_in_bytes)
    with open(FILE_PATH_UNDER_TEST, "rb") as f:
        file_service = FileService(
            requesting_user=file_user, db=test_db, app_settings=Settings()
        )

        result = file_service.upload_file(
            file_to_upload=f, user_id=file_user.id, file_name="simple-file.jpg"
        )
        assert isinstance(result, ServiceResult)
        assert not result.success, result.data
        assert isinstance(result.exception, FileTooLargeException)

    # * test with a custom passed file size
    with open(FILE_PATH_UNDER_TEST, "rb") as f:
        file_service = FileService(
            requesting_user=file_user, db=test_db, app_settings=Settings()
        )

        result = file_service.upload_file(
            file_to_upload=f,
            user_id=file_user.id,
            file_name="simple-file.jpg",
            file_size_limit=int((test_file_size_in_bytes - 1) / ONE_MEGA_BYTE),
        )
        assert isinstance(result, ServiceResult)
        assert not result.success, result.data
        assert isinstance(result.exception, FileTooLargeException)

    # * reset
    os.environ["MAX_SIZE_OF_A_FILE"] = f"{test_file_size_in_bytes / ONE_MEGA_BYTE}"

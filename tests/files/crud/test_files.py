from src.files.crud import FileCRUD
from src.models import Bucket, FileObject
from src.users.models import User


def test_save_file(test_db, file_user: User):
    file_crud = FileCRUD(test_db)
    file_saved = file_crud.save_file(
        "simple-file.jpg",
        original_file_name="simple-file.jpg",
        owner_id=file_user.id,  # type: ignore
    )
    assert isinstance(file_saved, FileObject)
    assert isinstance(file_saved.bucket, Bucket)
    assert file_saved.bucket.owner_id == file_user.id
    assert file_saved.original_file_name == "simple-file.jpg"
    assert file_saved.file_name == "simple-file.jpg"


def test_get_files(test_db, file_user: User):
    file_crud = FileCRUD(test_db)

    files = file_crud.get_files()
    assert len(files) > 0
    file_under_test = files[0]
    assert isinstance(file_under_test, FileObject)
    assert isinstance(file_under_test.bucket, Bucket)
    assert file_under_test.original_file_name == "simple-file.jpg"
    assert file_under_test.file_name == "simple-file.jpg"

    files = file_crud.get_files(original_file_name="simple")
    assert len(files) > 0

    files = file_crud.get_files(owner_id=file_user.id)  # type: ignore
    assert len(files) > 0


def test_get_file(test_db):
    file_crud = FileCRUD(test_db)

    files = file_crud.get_files()

    file_gotten = file_crud.get_file(
        file_id=files[0].id,  # type: ignore
    )
    assert isinstance(file_gotten, FileObject)


def test_remove_file(test_db):
    file_crud = FileCRUD(test_db)

    files = file_crud.get_files()

    file_id_under_test = files[0].id

    assert (
        file_crud.remove_file(
            file_id_under_test,  # type: ignore
        )
        == 1
    )

    assert (
        file_crud.get_file(
            file_id_under_test,  # type: ignore
        )
        == None
    )


def test_remove_files(test_db, file_user: User):
    file_crud = FileCRUD(test_db)
    file_ids = []
    x_files_create = 10
    for x in range(0, x_files_create):
        file_saved = file_crud.save_file(
            "simple-file.jpg",
            original_file_name="simple-file.jpg",
            owner_id=file_user.id,  # type: ignore
        )
        file_ids.append(file_saved.id)

    assert file_crud.remove_files(file_ids) == x_files_create

    for deleted_file_id in file_ids:
        assert file_crud.get_file(deleted_file_id) == None

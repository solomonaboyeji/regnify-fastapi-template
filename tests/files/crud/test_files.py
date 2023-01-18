from src.files.crud import FileCRUD
from src.models import FileObject
from src.users.models import User


def test_save_file(test_db, file_user: User):
    file_crud = FileCRUD(test_db)
    file_saved = file_crud.save_file(
        "simple-file.jpg",
        original_file_name="simple-file.jpg",
        owner_id=file_user.id,  # type: ignore
    )
    assert isinstance(file_saved, FileObject)
    assert file_saved.bucket.owner_id == file_user.id


def test_get_files():
    pass


def test_get_file():
    pass


def test_remove_file():
    assert 1 == 2


def test_remove_files():
    assert 1 == 2

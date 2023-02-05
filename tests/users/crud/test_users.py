from uuid import UUID
import pytest
from datetime import datetime, timedelta
from jose import jwt
from src.exceptions import GeneralException
from src.models import FileObject
from src.security import create_access_token, get_password_hash
from src.users.crud.users import UserCRUD
from src.users.models import Profile, User
from src.users.schemas import UserCreate, UserUpdate
from src.files.crud import FileCRUD
from src.config import Settings

from src.config import setup_logger

logger = setup_logger()


def test_create_access_token(app_settings):
    data = {
        "sub": "1@regnify.com",
        "is_active": True,
        "is_super_admin": False,
        "roles": [],
    }
    access_token_expires = timedelta(minutes=app_settings.access_code_expiring_minutes)
    token = create_access_token(
        data,
        expires_delta=access_token_expires,
        secret_key=app_settings.secret_key,
        algorithm=app_settings.algorithm,
    )

    payload = jwt.decode(
        token=token,
        key=app_settings.secret_key,
        algorithms=[app_settings.algorithm],
    )

    assert "sub" in payload
    assert payload["sub"] == "1@regnify.com"
    assert "is_active" in payload
    assert payload["is_active"]
    assert "is_super_admin" in payload
    assert not payload["is_super_admin"]
    assert "roles" in payload
    assert payload["roles"] == []


def test_create_user(test_db):
    access_begin = datetime.now()
    access_end = datetime.now() - timedelta(days=1)

    email_under_test = "3@regnify.com"
    users_crud: UserCRUD = UserCRUD(db=test_db)
    user: User = users_crud.create_user(
        UserCreate(email=email_under_test, last_name="1", first_name="2", password="3", access_begin=access_begin, access_end=access_end)  # type: ignore
    )
    assert user.email == email_under_test
    assert user.access_end == access_end
    assert user.access_begin == access_begin

    assert user.profile.photo_file == None


def test_create_user_with_existing_email(user_crud: UserCRUD):
    email_under_test = "3@regnify.com"

    with pytest.raises(GeneralException):
        user_crud.create_user(
            UserCreate(
                email=email_under_test, last_name="1", first_name="2", password="3"  # type: ignore
            )
        )


def test_update_user(user_crud: UserCRUD):
    email_under_test = "3@regnify.com"

    # * getting user with a wrong email address
    none_user = user_crud.get_user_by_email("no-user@regnify.com")
    assert none_user == None

    user = user_crud.get_user_by_email(email_under_test)
    assert user != None

    user_crud.update_user(
        user.id, UserUpdate(first_name="User3", last_name="3User", is_active=False, is_super_admin=False)  # type: ignore
    )

    updated_user: User = user_crud.get_user(user.id)  # type: ignore

    assert updated_user.email == email_under_test  # type: ignore
    assert isinstance(updated_user.profile, Profile)  # type: ignore
    assert updated_user.profile.last_name == "3User"  # type: ignore
    assert updated_user.profile.first_name == "User3"  # type: ignore
    assert not updated_user.is_active  # type: ignore
    assert not updated_user.is_super_admin  # type: ignore


def test_change_password(user_crud: UserCRUD):
    email_under_test = "3@regnify.com"
    old_user = user_crud.get_user_by_email(email_under_test)
    assert old_user != None
    old_hashed_password = old_user.hashed_password
    hashed_password = get_password_hash("new-password")
    new_user = user_crud.update_user_password(old_user.id, hashed_password)  # type: ignore
    assert new_user.hashed_password != old_hashed_password


def test_update_user_photo(
    user_crud: UserCRUD, crud_user: User, test_db, app_settings: Settings
):
    file_crud = FileCRUD(test_db)
    file_object = file_crud.save_file(
        "123-simple-file.png",
        original_file_name="simple-file.png",
        owner_id=crud_user.id,
        total_bytes=10,
        mime_type="application/octet-stream",
        extension="jpg",
        backend_storage=app_settings.backend_storage_option,
    )
    assert isinstance(file_object, FileObject)

    email_under_test = "3@regnify.com"
    old_user: User = user_crud.get_user_by_email(email_under_test)
    assert old_user != None

    profile = user_crud.update_user_profile_photo(
        UUID(str(crud_user.id)),
        file_object_id=UUID(str(file_object.id)),
    )
    assert isinstance(profile, Profile)
    assert profile.photo_file_id == file_object.id

    assert profile.photo_file.original_file_name == "simple-file.png"
    assert profile.photo_file.file_name == "123-simple-file.png"
    assert profile.photo_file.backend_storage == app_settings.backend_storage_option

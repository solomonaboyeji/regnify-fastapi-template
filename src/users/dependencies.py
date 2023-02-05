from cgi import print_form
from uuid import uuid4

4
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from src.auth.dependencies import get_current_active_user
from src.config import Settings
from src.database import get_db_sess
from src.service import get_settings
from src.users.config import get_default_avatar_url
from src.users.models import User
from src.users.permissions import CAN_CREATE_SPECIAL_USER, CAN_READ_ALL_USERS

from src.users.schemas import ProfileOut, UserOut
from src.users.services.roles import RolesService
from src.users.services.users import UserService

# * Permissions and permissions


def can_create_special_user(current_user: UserOut = Depends(get_current_active_user)):
    """Raises a 403 error if the user does not have the right privilege"""

    permission_found: bool = False
    for role in current_user.user_roles:
        if CAN_CREATE_SPECIAL_USER in role.permissions:  # type: ignore
            permission_found = True

    if not permission_found:
        raise HTTPException(
            status_code=403, detail="You are not permitted to perform this action."
        )


def can_read_all_users(current_user: UserOut = Depends(get_current_active_user)):
    """Raises a 403 error if the user does not have the right privilege"""

    permission_found: bool = False
    for role in current_user.user_roles:
        if CAN_READ_ALL_USERS in role.permissions:  # type: ignore
            permission_found = True

    if not permission_found:
        raise HTTPException(
            status_code=403, detail="You are not permitted to perform this action."
        )


def initiate_user_service(
    current_user: UserOut = Depends(get_current_active_user),
    db: Session = Depends(get_db_sess),
    app_settings: Settings = Depends(get_settings),
):
    return UserService(requesting_user=current_user, db=db, app_settings=app_settings)


def initiate_role_service(
    current_user: UserOut = Depends(get_current_active_user),
    db: Session = Depends(get_db_sess),
    app_settings: Settings = Depends(get_settings),
):
    return RolesService(requesting_user=current_user, db=db, app_settings=app_settings)


def anonymous_user():
    return UserOut(
        id=uuid4(),
        email="anonymous@regnify.com",  # type: ignore
        is_active=False,
        is_super_admin=False,
        user_roles=[],
        profile=ProfileOut(
            last_name="Anonymous",
            first_name="User",
            avatar_url=get_default_avatar_url("Anonymous", User),
            file_to_upload=None,
        ),
    )


def initiate_anonymous_user_service(
    db: Session = Depends(get_db_sess),
    app_settings: Settings = Depends(get_settings),
    anonymous_user=Depends(anonymous_user),
):
    return UserService(requesting_user=anonymous_user, db=db, app_settings=app_settings)  # type: ignore

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.users.permissions import CAN_CREATE_SPECIAL_USER, CAN_READ_ALL_USERS

from src.users.schemas import UserOut
from src.users.service import UserService

# * Permissions and permissions


def can_create_special_user(current_user: UserOut = Depends(get_current_active_user)):
    """Raises a 403 error if the user does not have the right privilege"""

    permission_found: bool = False
    for role in current_user.user_roles:
        if CAN_CREATE_SPECIAL_USER in role.permissions:
            permission_found = True

    if not permission_found:
        raise HTTPException(
            status_code=403, detail="You are not permitted to perform this action."
        )


def can_read_all_users(current_user: UserOut = Depends(get_current_active_user)):
    """Raises a 403 error if the user does not have the right privilege"""

    permission_found: bool = False
    for role in current_user.user_roles:
        if CAN_READ_ALL_USERS in role.permissions:
            permission_found = True

    if not permission_found:
        raise HTTPException(
            status_code=403, detail="You are not permitted to perform this action."
        )


def initiate_user_service(
    current_user: UserOut = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return UserService(requesting_user=current_user, db=db)

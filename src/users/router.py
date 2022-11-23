"""User's Router"""
from uuid import UUID
from fastapi import APIRouter, Depends, Header, Path

from src.auth.dependencies import get_current_active_user, has_admin_token_in_header
from src.database import get_db
from src.pagination import CommonQueryParams
from src.service import handle_result
from src.users import schemas
from src.users.dependencies import (
    can_create_special_user,
    can_read_all_users,
    initiate_user_service,
)
from src.users.schemas import ManyUsersInDB, UserOut
from src.users.service import UserService

router = APIRouter(tags=["Users"], prefix="/users")


@router.get(
    "/token",
    response_model=UserOut,
)
def read_user_me(current_user: UserOut = Depends(get_current_active_user)):
    return current_user


@router.post(
    "/create-special-user",
    dependencies=[Depends(has_admin_token_in_header), Depends(can_create_special_user)],
)
def create_special_user(username: str):
    """Creates Special User"""

    return {"username": username}


@router.post(
    "/unsecure",
    response_model=schemas.UserOut,
)
def create_user_unauthenticated(
    user: schemas.UserCreate,
    db=Depends(get_db),
):
    user_service = UserService(requesting_user=None, db=db)  # type: ignore
    result = user_service.create_user(user)
    return handle_result(result, schemas.UserOut)  # type: ignore


@router.post(
    "/",
    response_model=schemas.UserOut,
)
def create_user(
    user: schemas.UserCreate,
    user_service: UserService = Depends(initiate_user_service),
    admin_signup_token: str = Header(
        None,
        max_length=50,
        description="The correct admin token to admin only features",
    ),
):
    result = user_service.create_user(user, admin_signup_token=admin_signup_token)  # type: ignore
    return handle_result(result, schemas.UserOut)  # type: ignore


@router.put(
    "/{user_id}",
    response_model=schemas.UserOut,
)
def update_user(
    user: schemas.UserUpdate,
    user_id: UUID = Path(),
    user_service: UserService = Depends(initiate_user_service),
):
    result = user_service.update_user(user_id, user)  # type: ignore
    return handle_result(result, schemas.UserOut)  # type: ignore


@router.get(
    "/", response_model=ManyUsersInDB, dependencies=[Depends(can_read_all_users)]
)
def read_users(
    common: CommonQueryParams = Depends(),
    user_service: UserService = Depends(initiate_user_service),
):
    result = user_service.get_users(skip=common.skip, limit=common.limit)
    return handle_result(result, schemas.ManyUsersInDB)  # type: ignore


@router.get(
    "/{user_id}",
    response_model=schemas.UserOut,
)
def read_user(
    user_id: UUID,
    user_service: UserService = Depends(initiate_user_service),
):
    result = user_service.get_user_by_id(id=user_id)
    return handle_result(result, schemas.UserOut)  # type: ignore

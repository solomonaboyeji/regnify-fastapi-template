"""User's Router"""

from ctypes import resize
from uuid import UUID
from pydantic import EmailStr
from fastapi import APIRouter, Depends, Header, Path, Query
from src import mail as mail_funcs

from src.auth.dependencies import (
    get_current_active_user,
    has_admin_token_in_header,
    user_must_be_admin,
)
from src.config import setup_logger
from src.database import get_db
from src.service import AppResponseModel, failed_service_result
from src.pagination import CommonQueryParams
from src.service import handle_result, success_service_result
from src.users import schemas
from src.users.dependencies import (
    can_create_special_user,
    can_read_all_users,
    initiate_anonymous_user_service,
    initiate_user_service,
)
from src.users.schemas import ChangePasswordWithToken, ManyUsersInDB, UserOut
from src.users.service import UserService

router = APIRouter(tags=["Users"], prefix="/users")


logger = setup_logger()


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


@router.post("/request-password-change", response_model=AppResponseModel)
async def request_password_change(
    email: EmailStr = Query(),
    user_service: UserService = Depends(initiate_anonymous_user_service),
):
    success_message = "A reset password information has been sent to the associated account's email address."
    result_with_token = user_service.create_request_password(email)
    if result_with_token.success:
        user_with_email_result = user_service.get_user_by_email(email)
        if not user_with_email_result.success:
            logger.error("Unable to send email to user")
            return
        else:
            await mail_funcs.send_change_password_request_mail(
                user_with_email_result.data.email,
                subject="Password Change Request",
                reset_token=result_with_token.data,
            )

    return handle_result(success_service_result(success_message))  # type: ignore


@router.put("/change-user-password", response_model=AppResponseModel)
async def change_user_password(
    data: ChangePasswordWithToken,
    user_service: UserService = Depends(initiate_anonymous_user_service),
):
    result = user_service.change_password_with_token(data.token, data.new_password)
    if result.success:
        await mail_funcs.send_password_changed_mail(result.data.email)
        return handle_result(success_service_result("Your password has been successfully changed."))  # type: ignore

    return handle_result(result)


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


@router.put(
    "/{user_id}/admin-change-user-password",
    response_model=schemas.UserOut,
    dependencies=[Depends(user_must_be_admin)],
)
def admin_change_user_password(
    data: schemas.ChangePassword,
    user_id: UUID = Path(),
    user_service: UserService = Depends(initiate_user_service),
):
    result = user_service.update_user_password(user_id, data.password)
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

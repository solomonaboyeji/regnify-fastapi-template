"""User's Router"""

from io import BytesIO
from tempfile import NamedTemporaryFile

from uuid import UUID
from pydantic import EmailStr
from fastapi import APIRouter, Depends, Header, Path, Query, Security, UploadFile, File
from fastapi.responses import FileResponse
from src import mail as mail_funcs

from src.auth.dependencies import (
    get_current_active_user,
    user_must_be_admin,
)
from src.config import setup_logger
from src.files.schemas import FileObjectOut
from src.scopes import UserScope
from src.service import AppResponseModel, does_admin_token_match
from src.pagination import CommonQueryParams
from src.service import handle_result, success_service_result
from src.users import schemas
from src.users.dependencies import (
    can_read_all_users,
    initiate_anonymous_user_service,
    initiate_user_service,
)

from src.users.schemas import (
    ChangePasswordWithToken,
    ManySystemScopeOut,
    ManyUsersInDB,
    UserOut,
)
from src.users.services.users import UserService
from src.files.utils import prepare_file_for_http_upload

router = APIRouter(tags=["Users"], prefix="/users")


logger = setup_logger()


@router.get(
    "/token",
    response_model=UserOut,
)
def read_user_me(current_user: UserOut = Depends(get_current_active_user)):
    return current_user


@router.get(
    "/list-scopes",
    response_model=ManySystemScopeOut,
)
def list_scopes(
    user_service: UserService = Security(initiate_user_service, scopes=["me"])
):
    return ManySystemScopeOut.parse_obj({"scopes": user_service.get_system_scopes()})


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
    "/",
    response_model=schemas.UserOut,
)
async def create_user(
    user: schemas.UserCreate,
    user_service: UserService = Security(
        initiate_user_service, scopes=[UserScope.CREATE.value]
    ),
    admin_signup_token: str = Header(
        None,
        max_length=50,
        description="The correct admin token to use admin only features",
    ),
):
    """Allows a user to create another user in the system. The user is made active if the correct admin-signup-token is provided, and no email will be sent to the user."""

    result = user_service.create_user(user, admin_signup_token=admin_signup_token)  # type: ignore

    if result.success and not does_admin_token_match(admin_signup_token):
        await mail_funcs.send_new_account_info(
            user.email,
            password=user.password,
            owner_name=f"{user_service.requesting_user.profile.last_name} {user_service.requesting_user.profile.first_name}",
        )

    return handle_result(result, schemas.UserOut)  # type: ignore


@router.post(
    "/resend-invite",
    response_model=AppResponseModel,
)
async def resend_invite(
    email: EmailStr,
    user_service: UserService = Depends(initiate_anonymous_user_service),
):
    """Sends an email to the user on how to access their account again."""

    result = user_service.get_user_by_email(email)
    if result.success:
        await mail_funcs.send_how_to_change_password_email(email)  # type: ignore

    return handle_result(success_service_result("Check your email."))  # type: ignore


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


@router.get(
    "/{user_id}/download-photo",
    response_class=FileResponse,
)
def download_user_photo(
    user_id: UUID,
    user_service: UserService = Depends(initiate_user_service),
):
    result = user_service.download_user_photo(user_id=user_id)
    buffer: BytesIO = result.data[0]
    file_object: FileObjectOut = result.data[1]

    delete_immediately = False

    with NamedTemporaryFile(
        mode="w+b", suffix=file_object.extension, delete=delete_immediately
    ) as file_out:
        file_out.write(buffer.read())
        return FileResponse(
            file_out.name,
            media_type=file_object.mime_type,
            headers={"Cache-Control": "max-age=0"},
        )


@router.put("/{user_id}/upload-photo", response_model=schemas.ProfileOut)
def upload_user_photo(
    user_id: UUID,
    file_to_upload: UploadFile = File(...),
    user_service: UserService = Depends(initiate_user_service),
):

    the_file = prepare_file_for_http_upload(file_to_upload)

    result = user_service.upload_user_photo(
        user_id=user_id,
        file_to_upload=the_file,
        file_name=file_to_upload.filename,
    )
    return handle_result(result, schemas.ProfileOut)  # type: ignore

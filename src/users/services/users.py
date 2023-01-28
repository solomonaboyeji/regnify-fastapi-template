import datetime
from datetime import timedelta
from typing import Any, Union
from uuid import UUID

from jose import jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session
from src.config import Settings, setup_logger
from src.exceptions import BaseForbiddenException, GeneralException
from src.security import decode_token, get_password_hash
from src.service import (
    BaseService,
    ServiceResult,
    does_admin_token_match,
    failed_service_result,
    success_service_result,
)

from src.users import schemas
from src.users.crud.users import UserCRUD
from src.users.exceptions import DuplicateUserException, UserNotFoundException
from src.users.models import Profile, Roles, User


class UserService(BaseService):
    def __init__(
        self, requesting_user: schemas.UserOut, db: Session, app_settings: Settings
    ) -> None:
        super().__init__(requesting_user, db)
        self.users_crud = UserCRUD(db)
        self.app_settings: Settings = app_settings
        self.logger = setup_logger()

        if requesting_user is None:
            raise GeneralException("Requesting User was not provided.")

    def get_system_scopes(self):
        return [
            {"title": "user", "scopes": User.full_scopes()},
            {"title": "role", "scopes": Roles.full_scopes()},
            {"title": "profile", "scopes": Profile.full_scopes()},
        ]

    def update_user(
        self, id: UUID, user: schemas.UserUpdate
    ) -> ServiceResult[Union[User, None]]:
        try:
            if user.is_active is not None and not self.requesting_user.is_super_admin:
                return ServiceResult(
                    data=None,
                    success=False,
                    exception=BaseForbiddenException(
                        "You are not allowed to perform this action."
                    ),
                )

            updated_user = self.users_crud.update_user(id, user)
        except UserNotFoundException as raised_exception:
            return failed_service_result(raised_exception)

        return success_service_result(updated_user)

    def update_user_password(
        self, id: UUID, new_password: str
    ) -> ServiceResult[Union[User, None]]:
        hashed_password = get_password_hash(new_password)
        try:
            updated_user = self.users_crud.update_user_password(
                user_id=id, hashed_password=hashed_password
            )
        except UserNotFoundException as raised_exception:
            return failed_service_result(raised_exception)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

        return ServiceResult(data=updated_user, success=True)

    def create_user(
        self, user: schemas.UserCreate, admin_signup_token: str = None  # type: ignore
    ) -> ServiceResult[Union[User, None]]:
        db_user: User = self.users_crud.get_user_by_email(email=user.email)
        if db_user:
            return ServiceResult(
                data=None,
                success=False,
                exception=DuplicateUserException(
                    f"The email is already registered. Try another one."
                ),
            )
        try:
            should_make_active = False
            if does_admin_token_match(admin_signup_token):
                should_make_active = True
            else:
                user.is_super_admin = False

            if user.access_begin is None:
                user.access_begin = datetime.datetime.utcnow()
                user.access_end = None
            else:
                if user.access_end is None:
                    return failed_service_result(
                        exception=GeneralException("access_end must be provided")
                    )

                if user.access_begin > user.access_end:
                    return failed_service_result(
                        exception=GeneralException(
                            "access_begin must be less than access_end."
                        )
                    )

            created_user = self.users_crud.create_user(
                user, should_make_active, user.is_super_admin
            )
        except GeneralException as raised_exception:
            return failed_service_result(raised_exception)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

        return ServiceResult(data=created_user, success=True)

    def get_users(self, skip: int = 0, limit: int = 10) -> ServiceResult:
        try:
            db_users = self.users_crud.get_users(skip=skip, limit=limit)
            total_db_users = self.users_crud.get_total_users()

            users_data = {"total": total_db_users, "data": db_users}
            return ServiceResult(data=users_data, success=True)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def get_user_by_id(self, id: UUID) -> ServiceResult[Union[User, None]]:
        try:
            db_user: User = self.users_crud.get_user(id)  # type: ignore
            if not db_user:
                return ServiceResult(
                    data=None,
                    success=False,
                    exception=UserNotFoundException(f"User with ID {id} not found"),
                )

            return success_service_result(db_user)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def get_user_by_email(self, email: str) -> ServiceResult[Union[User, None]]:
        try:
            db_user: User = self.users_crud.get_user_by_email(email)  # type: ignore
            if not db_user:
                return ServiceResult(
                    data=None,
                    success=False,
                    exception=UserNotFoundException(
                        f"User with email {email} not found"
                    ),
                )
            return success_service_result(db_user)
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def create_request_password(self, email: str) -> ServiceResult[Union[str, None]]:
        try:
            result = self.get_user_by_email(email)
            if result.success:
                expires_in = datetime.datetime.utcnow() + timedelta(
                    minutes=self.app_settings.password_request_minutes
                )
                to_encode: dict[str, Any] = {
                    "sub": str(result.data.id),
                    "exp": expires_in,
                    "type": "PASSWORD_REQUEST",
                }
                encoded_jwt = jwt.encode(
                    to_encode,
                    self.app_settings.secret_key_for_tokens,
                    algorithm=self.app_settings.algorithm,
                )
                self.update_user_last_password_token(result.data.id, encoded_jwt)
                return success_service_result(encoded_jwt)
            return result
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def update_user_last_password_token(
        self, user_id: UUID, token: str
    ) -> ServiceResult[schemas.UserOut]:
        try:
            result = self.get_user_by_id(user_id)
            if result.success:
                user: User = result.data
                user.last_password_token = token  # type: ignore
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                return success_service_result(user)

            return failed_service_result(
                UserNotFoundException(f"The user with ID {user_id} does not exist.")
            )
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

    def change_password_with_token(
        self, token: str, new_password: str
    ) -> ServiceResult[Union[schemas.UserOut, None]]:
        try:
            payload = decode_token(
                token,
                self.app_settings.secret_key_for_tokens,
                self.app_settings.algorithm,
            )
        except ExpiredSignatureError:
            return failed_service_result(
                GeneralException("There is something wrong with the token.")
            )
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

        user_id = payload["sub"]
        expires_in = payload["exp"]
        expires_in_date = datetime.datetime.utcfromtimestamp(expires_in)
        todays_date = datetime.datetime.utcnow()

        if expires_in_date < todays_date:
            return failed_service_result(
                GeneralException("The token has expired. Please generate a new one.")
            )

        get_user_result = self.get_user_by_id(user_id)
        if not get_user_result.success:
            return failed_service_result(
                GeneralException("There is something wrong with the token.")
            )

        if get_user_result.data.last_password_token != token:
            return failed_service_result(
                GeneralException("The token has expired. Please generate a new one.")
            )

        try:
            updated_user = self.users_crud.update_user_password(
                user_id, get_password_hash(new_password)
            )
            self.update_user_last_password_token(user_id, "")
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            return failed_service_result(raised_exception)

        return success_service_result(updated_user)

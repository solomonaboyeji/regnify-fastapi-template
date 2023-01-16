"""User's Router"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from src.auth.schemas import AccessToken

from src.auth.dependencies import invalid_auth_credentials_exception
from src.config import Settings
from src.database import get_db_sess
from src.service import get_settings
from src.security import authenticate_user, create_access_token
from src.users.exceptions import UserNotFoundException
from src.users.schemas import UserUpdate
from src.users.services.users import UserService

router = APIRouter(tags=["Auth"])


@router.post("/token", response_model=AccessToken)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_sess),
    app_settings: Settings = Depends(get_settings),
):
    """
    Authenticates with the given credentials.

    **Note**, passwords are case sensitive.
    """

    try:
        user = authenticate_user(db, form_data.username, form_data.password)

        user_service = UserService(
            requesting_user=user, db=db, app_settings=app_settings
        )
        user_service.update_user(
            user.id,  # type: ignore
            UserUpdate(last_login=datetime.utcnow()),
        )

    except UserNotFoundException as raised_exception:
        raise invalid_auth_credentials_exception() from raised_exception

    access_token_expires = timedelta(minutes=app_settings.access_code_expiring_minutes)

    user_scopes = ["me"]
    for role in user.user_roles:
        for scope in role.role.permissions:
            user_scopes.append(scope)

    access_token_data = {
        "id": str(user.id),
        "sub": user.email,
        "is_active": user.is_active,
        "is_super_admin": user.is_super_admin,
        "roles": [
            {"title": role.role.title, "id": str(role.role.id)}
            for role in user.user_roles
        ],
        "scopes": user_scopes,
    }

    access_token = create_access_token(
        data=access_token_data,
        secret_key=app_settings.secret_key,
        algorithm=app_settings.algorithm,
        expires_delta=access_token_expires,
    )
    token = AccessToken(access_token=access_token)
    return token

"""Dependencies"""

from sqlalchemy.orm import Session

from jose import jwt, JWTError

from fastapi import Header, HTTPException, status, Depends
from src.auth.exceptions import INVALID_AUTH_CREDENTIALS_EXCEPTION
from src.auth.schemas import TokenData
from src.config import Settings
from src.database import get_db

from src.security import get_user, oauth2_scheme
from src.service import get_settings
from src.users.schemas import UserOut


def has_admin_token_in_header(admin_access_token: str = Header()):
    """Verifies if the header has an admin token"""

    if admin_access_token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin-Access-Token header invalid",
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    app_settings: Settings = Depends(get_settings),
):
    credentials_exception = INVALID_AUTH_CREDENTIALS_EXCEPTION

    try:
        payload = jwt.decode(
            token=token,
            key=app_settings.secret_key,
            algorithms=[app_settings.algorithm],
        )
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: UserOut = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return current_user

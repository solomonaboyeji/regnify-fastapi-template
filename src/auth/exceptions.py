from fastapi import HTTPException, status


def invalid_auth_credentials_exception(authenticate_value: str = "Bearer"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": f"{authenticate_value}"},
    )

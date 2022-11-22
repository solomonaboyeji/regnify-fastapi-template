from functools import lru_cache
from typing import Any
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.config import Settings
from src.exceptions import (
    BaseConflictException,
    BaseForbiddenException,
    BaseNotFoundException,
    GeneralException,
    handle_bad_request_exception,
    handle_conflict_exception,
    handle_forbidden_exception,
    handle_not_found_exception,
)

from src.users import schemas


@lru_cache()
def get_settings():
    return Settings()


class ServiceResult:
    def __init__(
        self, data: Any, success: bool, message: str = "", exception: Exception = None  # type: ignore
    ) -> None:
        self.data = data
        self.success = success
        self.message = message
        self.exception = exception

    def __str__(self) -> str:
        if self.success:
            return self.data
        else:
            return f"Exception: {self.exception.__str__()}"


class BaseService:
    def __init__(self, requesting_user: schemas.UserOut, db: Session) -> None:
        self.requesting_user = requesting_user
        self.db = db


def handle_result(result: ServiceResult, expected_schema: BaseModel):
    """Handles the result returned from any service in the application, both failures and successes."""

    if result.success:
        try:
            return expected_schema.from_orm(result.data)
        except Exception as raised_exception:
            handle_bad_request_exception(raised_exception)

    if isinstance(result.exception, GeneralException):
        handle_bad_request_exception(result.exception)
    elif isinstance(result.exception, BaseNotFoundException):
        handle_not_found_exception(result.exception)
    elif isinstance(result.exception, BaseConflictException):
        handle_conflict_exception(result.exception)
    elif isinstance(result.exception, BaseForbiddenException):
        handle_forbidden_exception(result.exception)
    else:
        handle_bad_request_exception(result.exception)

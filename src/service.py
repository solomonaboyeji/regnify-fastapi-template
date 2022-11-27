from functools import lru_cache
from typing import Any, Generic, TypeVar
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
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

_T = TypeVar("_T")


@lru_cache()
def get_settings():
    return Settings()


class AppResponseModel(BaseModel):
    detail: str


class ServiceResult(Generic[_T]):
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


def success_service_result(data: Any):
    return ServiceResult(data=data, success=True, exception=None)  # type: ignore


def failed_service_result(exception: Exception):  # type: ignore
    return ServiceResult(data=None, success=False, exception=exception)  # type: ignore


def handle_result(result: ServiceResult, expected_schema: BaseModel = None):  # type: ignore
    """Handles the result returned from any service in the application, both failures and successes."""

    if result.success:
        try:
            if expected_schema is not None:
                return expected_schema.from_orm(result.data)
            else:
                return AppResponseModel(detail=result.data)
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


def custom_openapi_with_scopes(app: FastAPI, settings: Settings):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        contact={"email": get_settings().admin_email},
        title=get_settings().app_name,
        version=get_settings().api_version,
        routes=app.routes,
    )

    if settings.display_scopes:
        paths_with_descriptions = []
        for endpoint in openapi_schema["paths"]:
            path = openapi_schema["paths"][endpoint]
            for method in path:
                method_data = path[method]
                if "security" in method_data:
                    for oa2pb in method_data["security"]:
                        for scope in oa2pb["OAuth2PasswordBearer"]:
                            try:
                                endpoint_method_value = openapi_schema["paths"][
                                    endpoint
                                ][method]

                                if (
                                    "description"
                                    not in openapi_schema["paths"][endpoint][method]
                                ):
                                    openapi_schema["paths"][endpoint][method][
                                        "description"
                                    ] = f"<strong>Scopes: </strong> {scope},"
                                else:
                                    if (
                                        not endpoint_method_value
                                        in paths_with_descriptions
                                    ):
                                        paths_with_descriptions.append(
                                            openapi_schema["paths"][endpoint][method]
                                        )
                                        openapi_schema["paths"][endpoint][method][
                                            "description"
                                        ] += f"""
                                        <br />
                                        <br />
                                        <strong>Scopes: </strong> {scope}, """
                                    else:
                                        openapi_schema["paths"][endpoint][method][
                                            "description"
                                        ] += (scope + ",  ")

                            except KeyError:
                                openapi_schema["paths"][endpoint][method][
                                    "description"
                                ] = f"<strong>Scopes: </strong> {scope},  "

    return openapi_schema

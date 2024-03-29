"""main.py"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.openapi import simplify_operation_ids

from src.auth.router import router as auth_router
from src.exceptions import GeneralException
from src.init_platform import init_platform
from src.users import models
from src.database import engine
from src.users.routers.users import router as user_router
from src.users.routers.roles import router as role_router
from src.config import setup_logger
from src.service import custom_openapi_with_scopes, get_settings
from src.database import open_db_connections, close_db_connections

from src.database import open_db_connections, close_db_connections

models.Base.metadata.create_all(bind=engine)

logger = setup_logger()

app = FastAPI(
    title=get_settings().app_name,
    docs_url=get_settings().doc_url,
    redoc_url=get_settings().redoc_url,
    openapi_url=get_settings().openapi_url,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    max_age=600,
    allow_headers=["*"],
    allow_origin_regex=get_settings().allow_origin_regex,
)


app.include_router(auth_router)
app.include_router(role_router)
app.include_router(user_router)

simplify_operation_ids(app)

app.openapi_schema = custom_openapi_with_scopes(app, get_settings())


@app.get("/")
def root():
    """An unauthenticated root endpoint"""

    return {"message": "Hello, Welcome to REGNIFY"}


@app.on_event("startup")
def check_dependencies():
    if not get_settings().is_database_credentials_set():
        logger.error("Database URL not configured")
        raise GeneralException("Database URL has not been configured.")

    init_platform()


@app.on_event("startup")
def open_database_connection_pools():
    open_db_connections()


@app.on_event("shutdown")
def close_database_connection_pools():
    close_db_connections()

from fastapi import Depends
from typing import Iterable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from src.config import Settings, setup_logger
from typing import Optional
from sqlalchemy.engine import Engine as Database

from sqlalchemy.orm import Session

from google.cloud.sql.connector import Connector

load_dotenv()

app_settings = Settings()

engine = create_engine(app_settings.get_full_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_sess_new_session():
    local_engine = create_engine(app_settings.get_full_database_url())
    return sessionmaker(autocommit=False, autoflush=False, bind=local_engine)


# Dependency
# def get_db_sess():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


logger = setup_logger()

_db_conn: Optional[Database] = None

# * https://github.com/tiangolo/fastapi/issues/726#issuecomment-557687526
def open_db_connections():
    global _db_conn
    _db_conn = get_engine()


def close_db_connections():
    global _db_conn
    if _db_conn:
        _db_conn.dispose()


def get_engine():
    if app_settings.sql_database_provider == "CLOUD_SQL":
        return create_engine(SQLALCHEMY_DATABASE_URL, creator=get_cloud_sql_conn)
    else:
        return create_engine(app_settings.get_full_database_url())


def get_cloud_sql_conn():
    connector = Connector()
    with Connector() as connector:
        conn = connector.connect(
            app_settings.cloud_sql_instance_name,
            "pg8000",
            user=app_settings.db_user,
            password=app_settings.db_password,
            db=app_settings.db_name,
        )
    return conn


SQLALCHEMY_DATABASE_URL = "postgresql+pg8000://"

# Dependency
def get_db():
    # get_db_sess_sess()
    db = get_db_sess()
    try:
        yield db
    finally:
        db.close()  # type: ignore


db_engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
Base = declarative_base()

# ***


def get_db_conn() -> Database:
    assert _db_conn != None, "The DB connection is None"
    if _db_conn is not None:
        return _db_conn

    # ! This is not good cause the connections might not be closed
    # ! Do not forget to close session
    # ! Or the database might throw error of too many connections.
    # return get_engine()


# This is the part that replaces sessionmaker
def get_db_sess(db_conn=Depends(get_db_conn)) -> Iterable[Session]:
    sess = Session(bind=db_conn)

    try:
        yield sess
    finally:
        sess.close()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from src.config import Settings

load_dotenv()

app_settings = Settings()

engine = create_engine(app_settings.get_full_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_new_session():
    local_engine = create_engine(app_settings.get_full_database_url())
    return sessionmaker(autocommit=False, autoflush=False, bind=local_engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

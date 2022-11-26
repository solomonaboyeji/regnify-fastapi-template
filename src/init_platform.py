import sys

# ? Allows this script read the src folder.
sys.path.append(".")

from src.database import SessionLocal
from src.config import Settings
from src.exceptions import GeneralException
from src.users.schemas import UserCreate
from src.users.service import UserCRUD
from src.config import setup_logger
from src.users import models
from src.database import engine


logger = setup_logger()

db = SessionLocal()
models.Base.metadata.create_all(bind=engine)

app_settings = Settings()

if not app_settings.is_database_credentials_set():
    raise GeneralException("Database URL not configured")

user_crud = UserCRUD(db)


def create_admin_user():
    logger.info("Creating Admin User")
    existing_admin_user = user_crud.get_user_by_email(app_settings.admin_email)
    if existing_admin_user:
        logger.info("Admin User already created.")
        return

    user_crud.create_user(
        UserCreate(
            email=app_settings.admin_email,  # type: ignore
            last_name=app_settings.admin_first_name,
            first_name=app_settings.admin_last_name,
            password=app_settings.admin_password,
        ),
        should_make_active=True,
        is_super_admin=True,
    )
    logger.info(
        f"{app_settings.admin_email} ==> {app_settings.admin_password} - admin user created!"
    )


if __name__ == "__main__":
    create_admin_user()

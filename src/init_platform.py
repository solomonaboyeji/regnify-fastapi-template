import sys

from src.users.crud.roles import RoleCRUD

# ? Allows this script read the src folder.
sys.path.append(".")

from src.database import SessionLocal
from src.config import Settings
from src.exceptions import BaseConflictException, GeneralException
from src.users.schemas import UserCreate
from src.users.services.users import UserCRUD
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
role_crud = RoleCRUD(db)


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


def create_default_roles():
    logger.info("Creating Default Roles")
    existing_admin_user = user_crud.get_user_by_email(app_settings.admin_email)
    if existing_admin_user:
        raise Exception(f"Admin {app_settings.admin_email} user does not exist")

    try:
        role_crud.create_role(
            "Users Management",
            permissions=models.User.full_scopes(),
            created_by=existing_admin_user,
        )
    except BaseConflictException:
        pass

    try:
        role_crud.create_role(
            "Roles Management",
            permissions=models.Roles.full_scopes(),
            created_by=existing_admin_user,
        )
    except BaseConflictException:
        pass


def init_platform():
    create_admin_user()
    create_default_roles()


if __name__ == "__main__":
    init_platform()
